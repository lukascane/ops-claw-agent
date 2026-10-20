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
