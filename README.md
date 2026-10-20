<div align="center">

# 🐾 OpsClaw: Agentic RAG & Infrastructure Tool-Calling Demo

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-005571?logo=fastapi)](https://fastapi.tiangolo.com/)
[![NVIDIA NIM](https://img.shields.io/badge/NVIDIA-NIM%20Ready-76B900?logo=nvidia)](https://build.nvidia.com/)
[![Pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC?logo=pytest)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*An event-driven AI Reliability & Operations Agent bridging RAG runbooks with real-time backend telemetry.*

</div>

---

## 🏗️ System Architecture

```text
 ┌───────────────┐     1. User Query      ┌─────────────────────────┐
 │               │ ──────────────────────>│                         │
 │  Developer /  │                        │     OpsClaw Agent       │
 │   On-Call     │ <───────────────────── │  (NVIDIA NIM / OpenAI)  │
 │               │     Grounded Answer    └───────────┬─────────────┘
 └───────────────/                                    │
                                           2. Tool-Calling Loop
                                                      │
                       ┌──────────────────────────────┼──────────────────────────────┐
                       ▼                              ▼                              ▼
             ┌──────────────────┐           ┌──────────────────┐           ┌──────────────────┐
             │ search_runbooks  │           │check_queue_metrics│          │trigger_remediation│
             │   (Hybrid RAG)   │           │ (Redis / BullMQ) │           │  (Auto-Scale)    │
             └──────────────────┘           └──────────────────┘           └──────────────────┘



🌟 Key Engineering Highlights
Multi-Step Tool-Calling Orchestration: Autonomous execution loop (OpsClawAgent) that chains telemetry inspection (check_queue_metrics), RAG knowledge retrieval (search_runbooks), and safe remediation dispatch (trigger_remediation).

Drop-In NVIDIA NIM & Open-Weight Compatibility: Uses the standard OpenAI SDK interface pointed at https://integrate.api.nvidia.com/v1 (meta/llama-3.3-70b-instruct) or OpenAI (gpt-4o-mini), plus a zero-dependency Deterministic Simulation Mode for instant local testing without API credit barriers.

Rigorous Evaluation Harness (evals.py): Quantitative benchmark measuring Tool Selection Recall, Answer Groundedness / Faithfulness, and End-to-End Latency across multi-hop operational scenarios.

Production Microservice Ready: Packaged with FastAPI (/v1/agent/query, /health, OpenAPI /docs) and a lightweight Dockerfile.

📊 Evaluation Benchmark Results
Test Scenario	Tool Recall	Groundedness	Latency	Status
eval-01-queue-remediation	100%	100%	< 5 ms	PASS
eval-02-oauth-diagnostics	100%	100%	< 5 ms	PASS
eval-03-nim-pgvector-rag	100%	100%	< 5 ms	PASS
Aggregate Score	100.0%	100.0%	—	EXCELLENT
🚀 Quickstart & Installation
Bash
# Clone the repository
git clone [https://github.com/lukascane/ops-claw-agent.git](https://github.com/lukascane/ops-claw-agent.git)
cd ops-claw-agent

# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# 1. Run unit & integration tests
pytest -v

# 2. Run the evaluation benchmark suite
python evals.py

# 3. Launch the FastAPI server (Swagger UI at http://localhost:8000/docs)
uvicorn server:app --reload --port 8000
👤 Author
Lukas Cane (Łukasz Trzciński) — AI & Backend Software Engineer (Berlin, Germany)

Focus: Agentic Workflows, Event-Driven RAG Pipelines, OAuth2 Integrations, and Cloud Infrastructure.
EOF

git add README.md
git commit -m "docs: reformat README with correct GFM spacing and layout"
git push origin main
