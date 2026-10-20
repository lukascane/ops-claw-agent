import json
from agent import OpsClawAgent, search_runbooks, check_queue_metrics

def test_rag_runbook_retrieval():
    res = json.loads(search_runbooks("NVIDIA NIM pgvector recall"))
    assert len(res["matches"]) > 0
    assert res["matches"][0]["id"] == "doc-nim-03"

def test_telemetry_tool():
    res = json.loads(check_queue_metrics("rag-ingestion-queue"))
    assert res["metrics"]["status"] == "DEGRADED"
    assert res["metrics"]["pending_jobs"] == 1480

def test_agent_multi_tool_remediation_workflow():
    agent = OpsClawAgent(use_mock=True)
    out = agent.run("Check rag-ingestion-queue and remediate per runbook.")
    tools_used = [t["tool"] for t in out["tool_calls"]]
    assert "check_queue_metrics" in tools_used
    assert "search_runbooks" in tools_used
    assert "trigger_remediation" in tools_used
    assert "doc-rag-01" in out["answer"]
