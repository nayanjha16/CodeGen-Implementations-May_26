# Executive Summary — CodeGen Studio

> Synced from `ai-workflow/research/summaries/project-summary.md` (research phase).

## Project Purpose

**CodeGen** ("CodeGen Studio") is a modular, reproducible, research-oriented project
for evaluating the small code language model **`Salesforce/codegen-350M-multi`** on two
database-query tasks:

1. **Natural Language → SQL** generation (text-to-SQL)
2. **SQL → MongoDB (NoSQL)** rule-based translation

It bundles an end-to-end interactive query pipeline (generate → validate → execute →
explain → translate), a benchmark evaluation harness (Spider, BIRD), experiment tracking
(MLflow), a REST API (FastAPI), and an interactive UI (Streamlit).

## Business / Project Goals

- Provide a **reproducible baseline** for a 350M-parameter code LLM on text-to-SQL.
- Demonstrate a **complete, teachable pipeline**: prompt building, decoding strategies,
  validation, execution-based evaluation, and metric reporting.
- Offer **multiple front ends** (API, Streamlit UI, CLI scripts, notebooks).
- Show **cross-paradigm translation** (relational SQL → document MongoDB) with explicit
  capability boundaries.
- Track experiments with **MLflow** for comparison across models/datasets/prompts.

## Architecture Overview

Layered Python architecture with strong separation of concerns and dependency injection:

- `src/models/` — HuggingFace CodeGen wrapper (lazy load, device resolution, greedy/beam).
- `src/text2sql/` — prompt builder, SQL generator, validator, executor.
- `src/sql2nosql/` — rule-based SQL→MongoDB translator + evaluator.
- `src/query_engine/` — full interactive pipeline orchestrator.
- `src/api/` — FastAPI app (6 endpoints) + Pydantic schemas.
- `src/utils/` — config (YAML), seeds, logging.
- `datasets/` — Spider & BIRD loaders + preprocessing/statistics.
- `evaluation/` — metrics, benchmark runner, MLflow tracker.
- `streamlit_app/` — 4-page UI.
- `scripts/`, `notebooks/` — tooling and demos.

## Tech Stack

Python 3.11 · PyTorch · Transformers · sqlparse · FastAPI/uvicorn/pydantic ·
Streamlit/plotly · MLflow (SQLite store) · SQLite · nltk/rouge-score/bert-score/codebleu ·
Docker + docker-compose.

## Core Workflows

1. **Interactive pipeline** — generate → validate → execute → translate → explain.
2. **Benchmark evaluation** — load → batch-generate → metrics → MLflow logging.
3. **SQL→MongoDB translation** — parse → build find()/aggregate() → warn on unsupported.
4. **Serving** — FastAPI API, Streamlit UI, Docker Compose (api/streamlit/mlflow).

## Maturity

Feature-complete for baseline / evaluation / demo. Not a fine-tuning project (training is
a placeholder). NoSQL translator is intentionally rule-based with documented limits.
