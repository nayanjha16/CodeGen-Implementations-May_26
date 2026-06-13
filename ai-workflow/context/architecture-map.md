# Architecture Map — CodeGen Studio

> Synced from `ai-workflow/research/architecture/architecture-map.md` (research phase).

## Modules

- `src.models.model_loader` — `CodeGenModel` HF wrapper + `load_model()` (lazy, greedy/beam).
- `src.text2sql` — `PromptBuilder`, `SQLGenerator`, `SQLValidator`, `SQLExecutor`.
- `src.sql2nosql` — `SQLToNoSQLTranslator`, `NoSQLEvaluator`.
- `src.query_engine.engine` — `QueryEngine` full pipeline.
- `src.api` — FastAPI `main.py` (6 endpoints) + `schemas.py`.
- `src.utils` — `config`, `seeds`, `logging`.
- `datasets` — `SpiderLoader`, `BirdLoader`, `preprocess`.
- `evaluation` — `EvaluationMetrics`, `BenchmarkRunner`, `MLflowTracker`.
- `streamlit_app.app` — 4-page UI.

## Dependency Direction

`configs → utils.config → {models, text2sql, sql2nosql} → query_engine → api`.
`evaluation.benchmark → {metrics, mlflow_tracker, datasets, text2sql.sql_generator}`.
`evaluation.metrics` lazily imports `text2sql.{validator,executor}` (no import cycles).
Heavy deps (`torch`, `transformers`, metric libs) deferred to call time with fallbacks.

## Service Boundaries

| Service | Entry | Port |
|---------|-------|------|
| REST API | `uvicorn src.api.main:app` | 8000 |
| Streamlit UI | `streamlit run streamlit_app/app.py` | 8501 |
| MLflow | `mlflow server` / SQLite store | 5000 |

API and UI are independent front ends; both import core library directly (UI does NOT
call the API over HTTP). Compose runs all three, sharing `./data` and `./mlruns` volumes.

## Data Flow

- **Interactive**: question+schema → generate(SQL) → validate → execute(SQLite) →
  translate(MongoDB) → explain → result dict.
- **Benchmark**: loader.load_split → generate_batch → db_resolver(db_id) →
  metrics.evaluate_all → MLflow run.
- **Standardization**: loaders → `{question, schema, sql, db_id[, difficulty]}`.

## Cross-cutting

Config (single YAML), reproducibility (`set_seeds`), shared `"codegen"` logger, graceful
metric/model degradation, DI-based testability with mock fixtures.
