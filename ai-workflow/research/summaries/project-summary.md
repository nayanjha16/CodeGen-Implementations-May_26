# Executive Summary — CodeGen Studio (PEFT / LoRA Research)

> **Research focus (2026-06-21):** Introduce **parameter-efficient fine-tuning (PEFT)
> via LoRA** for three sequential tasks — **text2sql**, **sql2nosql**, **nosql2doc** —
> using the TEND-style dataset under `data/TEND/`. This summary reflects the *current*
> codebase (the prior 2026-06-13 research describing FastAPI/Streamlit/`query_engine` is
> stale; those modules no longer exist).

## Project Purpose

**CodeGen Studio** is a modular, reproducible, research-oriented project for evaluating
small code language models on a **three-stage database query pipeline**:

1. **text2sql** — natural-language question + SQL schema → SQL query.
2. **sql2nosql** — SQL query + MongoDB schema → MongoDB shell query.
3. **nosql2doc** (`documentation`) — MongoDB query + schema + question → plain-English
   documentation.

Today the system is **baseline / evaluation only**. There is **no training or
fine-tuning code anywhere** in the repository. The PEFT/LoRA initiative adds the missing
fine-tuning capability so each task's quality can be improved over the zero-shot baseline.

## Business / Project Goals

- Improve task accuracy over the prompt-only baseline using **LoRA adapters** (small,
  cheap-to-train, swappable) rather than full fine-tuning.
- Train on the **TEND dataset** (`data/TEND/*.csv`) derived from Spider, which already
  contains aligned `(question, sql_schema, sql_query, nosql_schema, nosql_query,
  documentation)` columns — i.e. ready-made supervision for all three tasks.
- Keep the work **reproducible** (seeds, config-driven) and **resource-aware** (small
  base models, LoRA, CPU/MPS/CUDA portability).
- Reuse the existing **prompt builders** and **evaluation harness** so fine-tuned models
  are scored on the same metrics as the baseline (apples-to-apples comparison).

## Architecture Overview (current)

Clean layered Python package under `src/`, plus a standalone `TEND/` dataset-generation
package:

- **`src/models/`** — `CodeGenModel` HF wrapper (`AutoModelForCausalLM` /
  `AutoModelForSeq2SeqLM`), lazy load, device auto-resolve (cuda > mps > cpu), greedy/beam
  generation. `MODEL_CHECKPOINT` already lets the loader pick a checkpoint dir over the
  base model — the natural hook for serving fine-tuned adapters.
- **`src/text2sql/`** — `PromptBuilder`, `SQLGenerator`, `SQLValidator`, `SQLExecutor`.
- **`src/sql2nosql/`** — `NoSQLPromptBuilder`, `NoSQLGenerator`, rule-based
  `SQLToNoSQLTranslator`, `NoSQLEvaluator`.
- **`src/documentation/`** — `DocumentationPromptBuilder`, `DocumentationGenerator`,
  `DocumentationEvaluator`, `ReferenceDocumentationBuilder` (the nosql2doc task).
- **`src/evaluation/`** — `EvaluationMetrics` (EM, exec acc, syntax validity, BLEU,
  ROUGE-L, BERTScore, CodeBLEU, token-F1), `BenchmarkRunner` (runs all three tasks end to
  end), `MLflowTracker`, `qwen_evaluator`.
- **`src/datasets/`** — `SpiderLoader`, `BirdLoader`, `DatasetPreprocessor`.
- **`src/utils/`** — config (YAML + `.env`), device, paths, seeds, logging,
  `schema_conversion` (`derive_mongo_schema_json`).
- **`TEND/`** — `TENDDatasetBuilder` + Qwen doc generator/evaluator produce the
  supervised CSVs in `data/TEND/`.

There is **no training package** (`src/training/`, no `Trainer`, no `train.py`). This is
the primary gap the LoRA work must fill.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 |
| Model / NLP | PyTorch ≥2.0, Transformers ≥4.36, accelerate, sentencepiece |
| PEFT | **Not yet present** — `peft` (and optionally `trl`, `bitsandbytes`) to be added |
| Candidate base models (already cached in `models/base/`) | `Salesforce/codegen-350M-multi`, `Qwen/Qwen2.5-Coder-0.5B`, `Qwen/Qwen2.5-0.5B-Instruct`, `bigcode/starcoder2-3b`, `google-t5/t5-base`, `google-t5/t5-large` |
| Dataset gen | `sql-mongo-converter`, sqlparse, Qwen2.5-0.5B-Instruct (doc + judge) |
| Metrics | nltk, rouge-score, bert-score, codebleu |
| Tracking | MLflow ≥2.9 (SQLite store) |
| Config | PyYAML (`configs/default.yaml`) + `.env` (`MODEL_NAME`, paths) |
| Hardware | macOS dev host → MPS; CUDA when available; CPU fallback (slow) |

## Core Workflows (current)

### 1. TEND dataset generation (`TEND.run_tend` / `scripts/run_all_tend.py`)
Spider split → SQL DDL → Mongo schema → Mongo query (rule-based) → Qwen documentation →
Qwen semantic judge → timestamped `data/TEND/spider_<split>_<MMDD_HHMM>.csv` + summary.

### 2. Three-task baseline evaluation (`BenchmarkRunner.run_on_dataset`)
Generate SQL → derive/generate MongoDB → generate documentation; score each stage with
the full metric suite; optionally log to MLflow. Results land in `results/<run>/`.

### 3. Model loading & checkpoints
`load_model()` resolves `MODEL_CHECKPOINT` (under `models/checkpoints/`) before falling
back to the cached base model. **LoRA adapters will be saved here** and loaded for eval.

## Current Maturity & Gap for LoRA

- **Implemented:** dataset generation, prompt construction, generation, validation,
  metrics, MLflow, model caching, checkpoint-aware loading.
- **Missing for LoRA:** `peft` dependency, a training dataset/`Dataset` builder that turns
  TEND CSV rows into `(prompt, target)` pairs per task, a LoRA training loop
  (`Trainer`/`SFTTrainer` or custom), adapter save/merge, and adapter-aware loading in
  `CodeGenModel`.
- **Critical data caveat:** `data/TEND/` currently holds only **10 train + 10 validation
  rows** (smoke-test sized). A real LoRA run needs the **full Spider train split (~7k
  examples)** regenerated through `run_all_tend.py` first.

This summary is synced to `ai-workflow/context/project-summary.md`.
