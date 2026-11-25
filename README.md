# 🚀 AI Recruiting Copilot

An autonomous multi-agent recruitment orchestration platform built with **LangGraph**, **FastAPI**, **Qdrant Vector Database**, **PostgreSQL**, and **Next.js**.

---

## 🌟 Architectural Highlights

* **5-Agent LangGraph Directed Acyclic Graph (DAG):**
  1. **Resume Extraction Agent:** Layout-aware text extraction into strict Pydantic schemas using constrained decoding.
  2. **Skill Mapping Agent:** Normalizes messy variants (`"reactjs"`, `"k8s"`) into a canonical industry skill taxonomy.
  3. **Gap Analysis Agent:** Cross-references candidate competencies against Job Description criteria with citation grounding and hard prerequisite gating.
  4. **Parallel Question Generation Agent:** Fans out into concurrent execution for **Technical Gap Probes** and **Behavioral Leadership Rubrics**, merging via LangGraph state reducers.
  5. **Executive Scorecard Agent:** Synthesizes final recommendations (`STRONG_HIRE`, `HIRE`, `LEAN_HIRE`, `REJECT`) with actionable interview guides.
* **Qdrant Vector Database:** Approximate Nearest Neighbor (ANN) search across 500+ resumes using HNSW indexing and payload-based pre-filtering (`years_experience`, `tenant_id`).
* **Automated Testing Suite:** Comprehensive Pytest coverage testing agent state transitions, conditional fast-reject gates, vector search pre-filtering, and FastAPI endpoints.

---

## 📂 Directory Structure

```
projects/ai copilot/
├── backend/
│   ├── app/
│   │   ├── agents/          # 5 Autonomous Agent Nodes & Fallbacks
│   │   ├── graph/           # LangGraph StateGraph, Edges & Topology
│   │   ├── schemas/         # Pydantic Schemas & RecruiterState
│   │   ├── services/        # Qdrant Vector Client, Parser, DB
│   │   ├── config.py        # Environment & App Settings
│   │   └── main.py          # FastAPI REST API & Global Handlers
│   ├── tests/               # Automated Pytest Suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # Next.js 14 Recruiter Portal
├── docker-compose.yml       # FastAPI + Qdrant + PostgreSQL + Next.js
├── run_demo.py              # Standalone CLI Demo Runner
└── README.md
```

---

## ⚡ Quick Start: Running the CLI Demo

You can run the full multi-agent pipeline immediately in your terminal:

```bash
python run_demo.py
```

---

## 🧪 Running Automated Tests

Run the full automated test suite using `pytest`:

```bash
cd backend
pytest -v
```

Tests cover:
* ✅ Agent node schema extraction and heuristic fallbacks
* ✅ Skill canonicalization across aliases (`"reactjs" -> "React"`, `"k8s" -> "Kubernetes"`)
* ✅ Gap analysis scoring and non-negotiable prerequisite gating
* ✅ LangGraph DAG state reducers and parallel fan-in question merging
* ✅ Qdrant vector indexing, cosine similarity, and payload pre-filtering
* ✅ FastAPI REST API status codes and response models

---

## 🐳 Docker Deployment

To launch the complete microservices stack:

```bash
docker-compose up --build
```

* **FastAPI Backend:** `http://localhost:8000` (Swagger docs at `/docs`)
* **Qdrant Web Console:** `http://localhost:6333/dashboard`
* **Next.js Dashboard:** `http://localhost:3000`
