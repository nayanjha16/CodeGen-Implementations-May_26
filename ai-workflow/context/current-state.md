# Current State — CodeGen Studio

> Baseline established during the **research** phase. No implementation/changes made yet.

## Snapshot

- **Date**: 2026-06-13
- **Phase**: Project reorganized for separation of concerns
- **Layout**: All Python packages under `src/`; UI in `apps/`; data artifacts in `data/` subdirs; Docker in `docker/`

## What Exists

A feature-complete baseline/evaluation/demo system for `Salesforce/codegen-350M-multi`:

- **Text-to-SQL**: prompt builder, model wrapper (greedy/beam), generator, validator,
  executor — all implemented.
- **SQL→NoSQL**: rule-based MongoDB translator (SELECT/WHERE/ORDER BY/LIMIT/GROUP BY) +
  evaluator — implemented, with documented gaps (JOIN/HAVING/UNION/aggregations).
- **Query engine**: full interactive pipeline orchestrator — implemented.
- **Datasets**: Spider + BIRD loaders (auto-download) and preprocessing — implemented.
- **Evaluation**: full metric suite (EM, exec acc, syntax validity, BLEU, ROUGE-L,
  BERTScore, CodeBLEU), benchmark runner, MLflow tracker — implemented.
- **Serving**: FastAPI (6 endpoints) + Streamlit (4 pages) — implemented.
- **Tooling**: scripts (setup/baseline/demo + shell launchers), Docker/compose, notebooks,
  pytest suite (~679 lines / 10 modules) — implemented.

## Known Gaps (no fixes applied)

- No fine-tuning/training loop (`scripts/train.sh` is a placeholder).
- No real MongoDB execution (translator emits strings only).
- No CI; generation tests are fully mocked.
- Streamlit eval charts use hard-coded sample data.

## Notable Issues Found (for planning, not yet addressed)

- **High**: `/execute-query` + caller-supplied `db_path` = arbitrary SQL execution / file
  access (no auth/sandbox).
- **High**: `/interactive-query` rebuilds `QueryEngine` per call → repeated model reloads.
- **High**: `SpiderLoader._download_spider_data` can raise `NameError` (shutil import
  inside a conditional).
- **Medium**: `gdown` used but not in `requirements.txt`; MLflow store URI inconsistent across config/scripts/compose.
- (Full list: `ai-workflow/research/risks/risk-analysis.md`.)

## Validation Status

- Tests **not executed** during research (analysis only). pytest suite present and wired.
- No code modified.

## Environment Assumptions

- Python 3.11; `PYTHONPATH` must include project root.
- Network needed for first-run model/dataset downloads (~700MB model).
- SQLite-based execution; CPU-capable (slow) or CUDA.
