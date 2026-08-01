# Executive Summary

## Project Title

**CodeGen Fine-Tuning with PEFT & LoRA**

Fine-tuning `Salesforce/codegen-350M-multi` with Parameter-Efficient Fine-Tuning (PEFT) via LoRA on three database query tasks: Text→SQL, SQL→MongoDB, and NoSQL→Documentation — plus deployment on Cloud Run and an AI Database Agent capstone demo.

---

## Problem Statement

Modern database systems span relational (SQL) and document (NoSQL) stores. Developers and analysts need to:

1. Translate natural-language questions into SQL
2. Convert SQL queries to MongoDB shell syntax
3. Generate human-readable documentation for NoSQL queries

Large language models can perform these tasks, but full fine-tuning of multi-billion-parameter models is expensive. **Small code LMs (350M parameters)** are lightweight, but zero-shot performance on structured database tasks is often insufficient.

---

## Objectives

| # | Objective | Status |
|---|-----------|--------|
| 1 | Build a modular, reproducible pipeline for three database query tasks | ✅ Complete |
| 2 | Evaluate baseline (zero-shot) performance on a fixed benchmark | ✅ Complete |
| 3 | Fine-tune task-specific LoRA adapters (v1 smoke → v2/v3 full TEND) | ✅ Complete |
| 4 | Compare baseline vs fine-tuned with automated + execution + judge metrics | ✅ Complete |
| 5 | Publish adapters and deploy OpenAI-compatible API on Cloud Run | ✅ Complete (v3) |
| 6 | AI Database Agent orchestrating schema, API, and live DB execution | ✅ Complete |

---

## Approach

We use **PEFT / LoRA** on one shared base model. Each task gets its own adapter while base weights stay frozen.

```
Natural Language ──► [Text2SQL adapter] ──► SQL
SQL ──► [SQL2NoSQL adapter] ──► MongoDB query
MongoDB query ──► [NoSQL2Doc adapter] ──► Documentation
```

Tasks are **evaluated and trained independently** using gold supervision from TEND — predictions from one stage are never fed into the next during benchmarking.

**Production today:** LoRA **v3** (full TEND, r=32 + FFN, 10 epochs) on Cloud Run via `fastapi-deploy/codegen_api`.

---

## Key Contributions

1. **End-to-end research pipeline** — dataset loading, prompts, generation, validation, metrics, MLflow
2. **Prompt parity** — training prompts match inference prompts (unit-tested)
3. **Multi-metric evaluation** — exact match, **TEND execution accuracy**, structural similarity, CodeBLEU, Ollama judge
4. **Reproducible benchmark** — frozen 50-example Spider gold validation set
5. **Iterative LoRA ladder** — v1 smoke → v2 full TEND (r=16) → **v3 production** (r=32 + FFN)
6. **Production deployment** — Hub publish + Cloud Run multi-adapter API + **AI Database Agent**

---

## Key Results (LoRA v3 vs Baseline, n=50)

Evaluated on the frozen Spider gold validation set with **TEND Postgres/Mongo execution** and Ollama `gemma3:4b` documentation judge:

| Task | Metric | Baseline | LoRA v3 | Change |
|------|--------|----------|---------|--------|
| **Text2SQL** | Execution accuracy | 14% | **66%** | **+52 pp** |
| **SQL2NoSQL** | Execution accuracy | 22% | **86%** | **+64 pp** |
| **Documentation** | Judge score /10 | 8.33 | **8.82** | +0.49 |

Earlier milestones: **v1** proved the pipeline (50-row smoke); **v2** reached 60% / 74% exec on full TEND with r=16 and 5 epochs.

See [Results & Analysis](05-results-and-analysis.md) and [version-tracker.md](../reference/version-tracker.md).

---

## Limitations & Future Work

**Current limitations**

- 350M model ceiling on complex multi-table joins
- Cold-start latency on Cloud Run (~45–60 s after idle)
- Agent schema retrieval uses keyword matching (not embeddings)

**Possible next steps**

1. **Future LoRA runs** — hyperparameter or data refreshes from updated TEND gold
2. **MIN_INSTANCES=1** on Cloud Run for faster demos
3. **Embedding-based schema tool** in the agent
4. Full TEND test-split eval (`--full-split`) for extended analysis

---

## Tech Stack (Summary)

| Layer | Technology |
|-------|------------|
| Language | Python 3.11 |
| Model | HuggingFace Transformers, PEFT, TRL SFTTrainer |
| Base LM | Salesforce/codegen-350M-multi |
| Dataset | TEND (care2achieve/tend) — Spider + BIRD |
| Metrics | EM, TEND execution, structural similarity, CodeBLEU, gemma3:4b judge |
| API | `fastapi-deploy/codegen_api` on Google Cloud Run |
| Agent | LangGraph + MCP + Web UI (`agent/`) |
| Tracking | MLflow (SQLite) |
| Config | YAML + `.env` |
