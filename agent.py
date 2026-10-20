import os
import json
import math
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

RUNBOOK_DOCS = [
    {
        "id": "doc-rag-01",
        "title": "BullMQ & Redis Event-Driven Queue Backpressure Runbook",
        "content": (
            "When the 'rag-ingestion-queue' exceeds 1,000 pending jobs or latency > 2500ms, "
            "it indicates embedding worker saturation. Remediation: execute trigger_remediation "
            "with action='scale_bullmq_workers' and target='rag-ingestion-queue'. Verify Redis memory stays below 80%."
        ),
        "keywords": ["bullmq", "redis", "queue", "rag-ingestion-queue", "latency", "backpressure", "workers", "embedding"]
    },
    {
        "id": "doc-oauth-02",
        "title": "OAuth2 Token Refresh & External Integration Failure Runbook",
        "content": (
            "HTTP 401/403 spikes on external connectors (Google Workspace / Slack OAuth2) usually stem "
            "from expired rotation keys or rate-limiting on the auth provider. Remediation: execute "
            "trigger_remediation with action='rotate_oauth_cache' and target='oauth-token-service'."
        ),
        "keywords": ["oauth2", "token", "401", "403", "auth", "connector", "integration", "rotate_oauth_cache"]
    },
    {
        "id": "doc-nim-03",
        "title": "NVIDIA NIM & pgvector Embedding Drift Runbook",
        "content": (
            "If semantic search recall drops below 0.85 after upgrading the NIM embedding microservice, "
            "ensure the vector dimension (1024 vs 1536) and cosine distance operator (<=> in pgvector) match "
            "the active model profile. Re-index stale partitions via the async backfill worker."
        ),
        "keywords": ["nvidia", "nim", "pgvector", "embedding", "recall", "vector", "cosine", "dimension"]
    }
]

def search_runbooks(query: str, top_k: int = 2) -> str:
    query_tokens = set(query.lower().replace("-", " ").split())
    scored = []
    for doc in RUNBOOK_DOCS:
        doc_tokens = set(doc["content"].lower().replace("-", " ").split()) | set(doc["keywords"])
        overlap = len(query_tokens.intersection(doc_tokens))
        score = overlap / (math.sqrt(len(query_tokens) or 1) * math.sqrt(len(doc_tokens) or 1))
        for kw in doc["keywords"]:
            if kw in query.lower():
                score += 0.25
        scored.append((round(score, 3), doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    results = [
        {"id": d["id"], "title": d["title"], "score": s, "content": d["content"]}
        for s, d in scored[:top_k] if s > 0
    ]
    return json.dumps({"matches": results or RUNBOOK_DOCS[:1]})

LIVE_TELEMETRY = {
    "rag-ingestion-queue": {
        "status": "DEGRADED",
        "pending_jobs": 1480,
        "avg_latency_ms": 3120,
        "redis_memory_pct": 64,
        "active_workers": 2
    },
    "oauth-token-service": {
        "status": "HEALTHY",
        "error_rate_401_pct": 0.2,
        "active_integrations": 42,
        "avg_latency_ms": 85
    }
}

def check_queue_metrics(service_name: str) -> str:
    key = service_name.strip().lower()
    for k, v in LIVE_TELEMETRY.items():
        if k in key or key in k:
            return json.dumps({"service": k, "metrics": v})
    return json.dumps({"error": f"Service '{service_name}' not found.", "available": list(LIVE_TELEMETRY.keys())})

def trigger_remediation(target: str, action: str, dry_run: bool = True) -> str:
    return json.dumps({
        "status": "SUCCESS",
        "target": target,
        "action_executed": action,
        "dry_run": dry_run,
        "audit_note": f"Remediation '{action}' dispatched to '{target}' (dry_run={dry_run})."
    })

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_runbooks",
            "description": "Search engineering RAG runbooks for troubleshooting queues, OAuth2, or NVIDIA NIM / pgvector.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query keywords"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_queue_metrics",
            "description": "Fetch live telemetry (pending jobs, latency, status) for a backend service or queue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "Service identifier, e.g. 'rag-ingestion-queue' or 'oauth-token-service'"
                    }
                },
                "required": ["service_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_remediation",
            "description": "Trigger an automated infrastructure remediation action based on runbook guidance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Target service name"},
                    "action": {"type": "string", "description": "Remediation action name from runbook"},
                    "dry_run": {"type": "boolean", "description": "Run safely in simulation mode"}
                },
                "required": ["target", "action"]
            }
        }
    }
]

TOOL_REGISTRY = {
    "search_runbooks": search_runbooks,
    "check_queue_metrics": check_queue_metrics,
    "trigger_remediation": trigger_remediation,
}

class OpsClawAgent:
    def __init__(self, use_mock: Optional[bool] = None):
        self.api_key = os.getenv("NVIDIA_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv(
            "LLM_BASE_URL",
            "https://integrate.api.nvidia.com/v1" if os.getenv("NVIDIA_API_KEY") else "https://api.openai.com/v1"
        )
        self.model = os.getenv(
            "LLM_MODEL",
            "meta/llama-3.3-70b-instruct" if os.getenv("NVIDIA_API_KEY") else "gpt-4o-mini"
        )
        self.use_mock = use_mock if use_mock is not None else (not bool(self.api_key))
        if not self.use_mock:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def run(self, user_prompt: str, max_turns: int = 4) -> Dict[str, Any]:
        tool_trace: List[Dict[str, Any]] = []

        if self.use_mock:
            return self._run_deterministic_agent(user_prompt, tool_trace)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are OpsClaw, a production AI Reliability & RAG Agent. "
                    "Always inspect live metrics or search runbooks using tools before diagnosing or remediating. "
                    "Cite specific numbers and runbook IDs in your concise technical response."
                )
            },
            {"role": "user", "content": user_prompt}
        ]

        for _ in range(max_turns):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                temperature=0.0
            )
            msg = response.choices[0].message
            messages.append(msg)

            if not msg.tool_calls:
                return {
                    "answer": msg.content or "",
                    "tool_calls": tool_trace,
                    "provider": self.base_url,
                    "model": self.model
                }

            for tc in msg.tool_calls:
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments or "{}")
                fn = TOOL_REGISTRY.get(fn_name)
                output = fn(**fn_args) if fn else json.dumps({"error": "Unknown tool"})
                tool_trace.append({"tool": fn_name, "args": fn_args, "output": json.loads(output)})
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": fn_name,
                    "content": output
                })

        return {
            "answer": "Max agent turns reached.",
            "tool_calls": tool_trace,
            "provider": self.base_url,
            "model": self.model
        }

    def _run_deterministic_agent(self, prompt: str, trace: List[Dict[str, Any]]) -> Dict[str, Any]:
        p_low = prompt.lower()
        if "rag-ingestion-queue" in p_low or "queue" in p_low or "bullmq" in p_low:
            m_out = json.loads(check_queue_metrics("rag-ingestion-queue"))
            trace.append({"tool": "check_queue_metrics", "args": {"service_name": "rag-ingestion-queue"}, "output": m_out})
            r_out = json.loads(search_runbooks("bullmq rag-ingestion-queue latency backpressure"))
            trace.append({"tool": "search_runbooks", "args": {"query": "bullmq rag-ingestion-queue latency backpressure"}, "output": r_out})
            if "remediat" in p_low or "fix" in p_low or "scale" in p_low:
                rem_out = json.loads(trigger_remediation("rag-ingestion-queue", "scale_bullmq_workers", True))
                trace.append({
                    "tool": "trigger_remediation",
                    "args": {"target": "rag-ingestion-queue", "action": "scale_bullmq_workers", "dry_run": True},
                    "output": rem_out
                })
            return {
                "answer": (
                    "Telemetry shows `rag-ingestion-queue` is DEGRADED with 1,480 pending jobs and 3,120ms avg latency "
                    "(Redis memory at 64%). Per runbook `doc-rag-01`, this exceeds the 1,000-job threshold due to "
                    "embedding worker saturation. Triggered `scale_bullmq_workers` on `rag-ingestion-queue`."
                ),
                "tool_calls": trace,
                "provider": "deterministic-local-sim",
                "model": "ops-claw-policy-v1"
            }

        if "oauth" in p_low or "401" in p_low:
            m_out = json.loads(check_queue_metrics("oauth-token-service"))
            trace.append({"tool": "check_queue_metrics", "args": {"service_name": "oauth-token-service"}, "output": m_out})
            r_out = json.loads(search_runbooks("oauth2 token 401 rotation"))
            trace.append({"tool": "search_runbooks", "args": {"query": "oauth2 token 401 rotation"}, "output": r_out})
            return {
                "answer": (
                    "Checked `oauth-token-service`: status is HEALTHY (0.2% 401 error rate, 85ms latency). "
                    "Per runbook `doc-oauth-02`, if 401/403 spikes occur, execute `rotate_oauth_cache` on `oauth-token-service`."
                ),
                "tool_calls": trace,
                "provider": "deterministic-local-sim",
                "model": "ops-claw-policy-v1"
            }

        r_out = json.loads(search_runbooks(prompt))
        trace.append({"tool": "search_runbooks", "args": {"query": prompt}, "output": r_out})
        top_doc = r_out["matches"][0]
        return {
            "answer": f"According to `{top_doc['id']}` ({top_doc['title']}): {top_doc['content']}",
            "tool_calls": trace,
            "provider": "deterministic-local-sim",
            "model": "ops-claw-policy-v1"
        }
