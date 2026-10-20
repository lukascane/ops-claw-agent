# OpsClaw: Agentic RAG & Infrastructure Tool-Calling Demo

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

An event-driven AI Reliability & Operations Agent built with **Python**, **OpenAI-compatible Tool Calling (NVIDIA NIM / Nebius / OpenAI)**, **Hybrid RAG Runbook Retrieval**, and an **Automated Evaluation Harness**.

Built to demonstrate production AI engineering patterns: connecting LLMs to real-time backend telemetry (BullMQ/Redis, OAuth2 services), grounding decisions in technical runbooks via RAG, and verifying agent behavior with deterministic `pytest` and evaluation metrics.

## Key Engineering Highlights

* **Multi-Step Tool-Calling Orchestration:** Autonomous execution loop (`OpsClawAgent`) that chains telemetry inspection (`check_queue_metrics`), RAG knowledge retrieval (`search_runbooks`), and safe remediation dispatch (`trigger_remediation`).
* **Drop-In NVIDIA NIM & Open-Weight Compatibility:** Uses the standard OpenAI SDK interface pointed at `[https://integrate.api.nvidia.com/v1](https://integrate.api.nvidia.com/v1)` (`meta/llama-3.3-70b-instruct`) or OpenAI (`gpt-4o-mini`), plus a zero-dependency **Deterministic Simulation Mode** so CI/CD tests and local demos run immediately without burning API credits.
* **Built-In Evaluation Workflow (`evals.py`):** Quantitative benchmark measuring **Tool Selection Recall**, **Answer Groundedness / Faithfulness**, and **End-to-End Latency** across multi-hop operational scenarios.
* **Production Microservice Ready:** Packaged with **FastAPI** (`/v1/agent/query`, `/health`, OpenAPI `/docs`) and a lightweight **Dockerfile**.

## Quickstart

    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    pytest -v
    python evals.py
    uvicorn server:app --reload --port 8000

## Author

**Lukas Cane** — AI & Backend Software Engineer (Berlin, Germany)


