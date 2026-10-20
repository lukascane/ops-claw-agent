import time
from agent import OpsClawAgent

EVAL_DATASET = [
    {
        "id": "eval-01-queue-remediation",
        "prompt": "Check rag-ingestion-queue health, look up the runbook, and fix the issue.",
        "expected_tools": ["check_queue_metrics", "search_runbooks", "trigger_remediation"],
        "expected_facts": ["1,480", "doc-rag-01", "scale_bullmq_workers"]
    },
    {
        "id": "eval-02-oauth-diagnostics",
        "prompt": "Check oauth-token-service metrics and summarize the OAuth2 401 runbook.",
        "expected_tools": ["check_queue_metrics", "search_runbooks"],
        "expected_facts": ["HEALTHY", "doc-oauth-02", "rotate_oauth_cache"]
    },
    {
        "id": "eval-03-nim-pgvector-rag",
        "prompt": "Why would semantic search recall drop below 0.85 after an NVIDIA NIM embedding upgrade?",
        "expected_tools": ["search_runbooks"],
        "expected_facts": ["doc-nim-03", "pgvector", "1024"]
    }
]

def evaluate_suite():
    agent = OpsClawAgent()
    print(f"\n=== Running OpsClaw Agent Evaluation Suite (Provider: {agent.model}) ===")
    print(f"{'Test ID':<28} | {'Tool Recall':<12} | {'Groundedness':<13} | {'Latency':<8} | {'Status'}")
    print("-" * 78)

    total_tool_score = 0.0
    total_ground_score = 0.0

    for case in EVAL_DATASET:
        t0 = time.time()
        res = agent.run(case["prompt"])
        latency_ms = int((time.time() - t0) * 1000)

        called_tools = [t["tool"] for t in res["tool_calls"]]
        matched_tools = [t for t in case["expected_tools"] if t in called_tools]
        tool_recall = len(matched_tools) / len(case["expected_tools"])

        answer_lower = res["answer"].lower()
        matched_facts = [f for f in case["expected_facts"] if f.lower() in answer_lower]
        groundedness = len(matched_facts) / len(case["expected_facts"])

        total_tool_score += tool_recall
        total_ground_score += groundedness
        passed = "PASS" if (tool_recall == 1.0 and groundedness >= 0.66) else "FAIL"

        print(f"{case['id']:<28} | {tool_recall:>10.0%}  | {groundedness:>11.0%}  | {latency_ms:>5} ms | {passed}")

    n = len(EVAL_DATASET)
    print("-" * 78)
    print(f"Aggregate Tool Selection Recall : {total_tool_score / n:.1%}")
    print(f"Aggregate Answer Groundedness   : {total_ground_score / n:.1%}\n")

if __name__ == "__main__":
    evaluate_suite()
