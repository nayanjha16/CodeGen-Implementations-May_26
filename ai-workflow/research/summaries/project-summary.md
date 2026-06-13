# Executive Summary — CodeGen Studio

## Project Purpose

**CodeGen** ("CodeGen Studio") is a modular, reproducible, research-oriented project
for evaluating the small code language model **`Salesforce/codegen-350M-multi`** on two
database-query tasks:

1. **Natural Language → SQL** generation (text-to-SQL)
2. **SQL → MongoDB (NoSQL)** rule-based translation

It bundles an end-to-end interactive query pipeline (generate → validate → execute →
explain → translate), a benchmark evaluation harness (Spider, BIRD), experiment tracking
(MLflow), a REST API (FastAPI), and an interactive UI (Streamlit). The repository
appears to back an academic/training deliverable (a `demo_presentation.py` references an
"IIT Hyderabad AIML Training" demo).

## Business / Project Goals

- Provide a **reproducible baseline** for a 350M-parameter code LLM on text-to-SQL.
- Demonstrate a **complete, teachable pipeline**: prompt building, decoding strategies,
  validation, execution-based evaluation, and metric reporting.
- Offer **multiple front ends** (API, Streamlit UI, CLI scripts, notebooks) so the same
  core logic can be demoed or integrated.
- Show **cross-paradigm translation** (relational SQL → document MongoDB) with explicit
  capability boundaries (warnings for unsupported constructs).
- Track experiments with **MLflow** for comparison across models, datasets, prompts, and
  decoding strategies.

## Architecture Overview

A clean layered Python architecture with strong separation of concerns:

- **`src/models/`** — `CodeGenModel` wrapper around HuggingFace `AutoModelForCausalLM`
  with lazy loading, device resolution (auto/cuda/cpu), and greedy/beam decoding.
- **`src/text2sql/`** — prompt building, SQL generation, validation (sqlparse + SQLite
  `EXPLAIN`), and execution (SQLite with order-independent row comparison).
- **`src/sql2nosql/`** — rule-based SQL→MongoDB translator (AST via sqlparse + regex
  fallbacks) and a translation-quality evaluator.
- **`src/query_engine/`** — orchestrates the full interactive pipeline.
- **`src/api/`** — FastAPI app exposing 6 endpoints with Pydantic schemas.
- **`src/utils/`** — config loading (YAML), seed setting, logging.
- **`datasets/`** — Spider & BIRD loaders (auto-download + schema parsing) and a
  preprocessor with cleaning, splitting, and statistics.
- **`evaluation/`** — metrics (EM, execution accuracy, syntax validity, BLEU, ROUGE-L,
  BERTScore, CodeBLEU), a `BenchmarkRunner`, and an `MLflowTracker`.
- **`streamlit_app/`** — 4-page UI (Text-to-SQL, SQL-to-NoSQL, Interactive, Evaluation).
- **`scripts/`** — setup, baseline eval, demo, and shell launchers.
- **`tests/`** — pytest suite (~679 lines across 10 test modules) with mock model and
  temp DB fixtures.

Dependency injection is used throughout (constructors accept optional collaborators),
which makes the code highly testable. Heavy imports (`torch`, `transformers`, metric
libraries) are deferred to call time, and metric computations degrade gracefully to a
token-overlap fallback when optional libraries are missing.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 |
| Model / NLP | PyTorch ≥2.0, Transformers ≥4.36, accelerate, sentencepiece |
| Model | `Salesforce/codegen-350M-multi` (configurable causal LM) |
| SQL parsing | sqlparse ≥0.4.4 |
| Datasets | HF `datasets`, `requests` (+ optional `gdown` for full Spider) |
| Metrics | nltk (BLEU), rouge-score, bert-score, codebleu |
| Tracking | MLflow ≥2.9 (SQLite backend store) |
| API | FastAPI ≥0.109, uvicorn, pydantic ≥2.5 |
| UI | Streamlit ≥1.30, plotly |
| Storage | SQLite (execution + sample DBs) |
| Config | PyYAML (`configs/default.yaml`) |
| Testing | pytest, pytest-cov, httpx |
| Packaging | Dockerfile (python:3.11-slim) + docker-compose (api, streamlit, mlflow) |

## Core Workflows

### 1. Interactive Query Pipeline (`QueryEngine.process`)
NL question + schema → **generate SQL** (CodeGen) → **validate** (syntax/completeness/
SQLite EXPLAIN) → **execute** (if DB + valid) → **translate to MongoDB** → **explain**
(human-readable summary). Returns a single dict consumed by the API and Streamlit UI.

### 2. Benchmark Evaluation (`BenchmarkRunner.run_on_dataset`)
Load standardized examples (Spider/BIRD) → batch-generate SQL → compute full metric
suite → resolve per-example SQLite DB paths for execution accuracy → log run to MLflow
(model, dataset, prompt template, decoding strategy, metrics).

### 3. SQL → MongoDB Translation (`SQLToNoSQLTranslator.translate`)
Parse SQL → extract table/columns/WHERE/ORDER BY/LIMIT/GROUP BY → build `db.coll.find(...)`
or `db.coll.aggregate([...])` string + structured filter/projection → emit warnings for
unsupported constructs (JOIN, HAVING, UNION, write statements).

### 4. Serving
- **API**: `uvicorn src.api.main:app` — `/health`, `/generate-sql`, `/translate-nosql`,
  `/execute-query`, `/evaluate`, `/interactive-query`.
- **UI**: `streamlit run streamlit_app/app.py`.
- **Docker**: `docker-compose up` brings up API (8000), Streamlit (8501), MLflow (5000).

## Current Maturity

The project is **feature-complete for a baseline/evaluation/demo** use case: all modules
exist, are wired together, and are covered by tests. It is **not** a fine-tuning project
(training is an explicit placeholder in `scripts/train.sh`) and the NoSQL translator is
intentionally rule-based with documented limitations.
