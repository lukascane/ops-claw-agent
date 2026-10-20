from fastapi import FastAPI
from pydantic import BaseModel
from agent import OpsClawAgent

app = FastAPI(
    title="OpsClaw Agentic RAG & Tool-Calling API",
    description="Production AI Agent demo integrating Hybrid RAG, Telemetry Tool Calling, and NVIDIA NIM / OpenAI endpoints.",
    version="1.0.0"
)
agent = OpsClawAgent()

class QueryRequest(BaseModel):
    prompt: str

@app.get("/health")
def health():
    return {"status": "ok", "model": agent.model, "mock_mode": agent.use_mock}

@app.post("/v1/agent/query")
def query_agent(req: QueryRequest):
    return agent.run(req.prompt)
