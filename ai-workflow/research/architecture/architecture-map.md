# Architecture Map — CodeGen Studio

## 1. Module Overview

| Package | Module | Responsibility |
|---------|--------|----------------|
| `src.models` | `model_loader.py` | `CodeGenModel` HF wrapper; `load_model()` factory. Lazy load, device resolve, greedy/beam generation. |
| `src.text2sql` | `prompt_builder.py` | `PromptBuilder` — schema+question → prompt; batch; template name for tracking. |
| | `sql_generator.py` | `SQLGenerator` — orchestrates model + prompt; extracts SQL from raw output (regex/code-fence). |
| | `sql_validator.py` | `SQLValidator` — syntax (sqlparse), completeness (parens, SELECT/FROM), SQLite `EXPLAIN`. |
| | `sql_executor.py` | `SQLExecutor` — run SQL on SQLite; order-independent result comparison. |
| `src.sql2nosql` | `translator.py` | `SQLToNoSQLTranslator` — SQL→MongoDB find()/aggregate(); warnings for unsupported. |
| | `evaluator.py` | `NoSQLEvaluator` — translation accuracy (exact/token-F1), structural equivalence. |
| `src.query_engine` | `engine.py` | `QueryEngine` — full pipeline: generate→validate→execute→translate→explain. |
| `src.api` | `main.py` | FastAPI app; 6 endpoints; `lru_cache` singletons. |
| | `schemas.py` | Pydantic request/response models. |
| `src.utils` | `config.py` | `load_config()` YAML loader; `get_project_root()`. |
| | `seeds.py` | `set_seeds()` for random/numpy/torch. |
| | `logging.py` | `setup_logging()` — "codegen" logger. |
| `datasets` | `spider_loader.py` | `SpiderLoader` — download (GitHub + gdown mirror), schema parse, splits, DB path resolve. |
| | `bird_loader.py` | `BirdLoader` — download (DAMO-ConvAI), evidence schema, splits, DB path resolve. |
| | `preprocess.py` | `DatasetPreprocessor`, `clean_sql/clean_question`, `compute_statistics`. |
| `evaluation` | `metrics.py` | `EvaluationMetrics` — EM, exec acc, syntax validity, BLEU, ROUGE-L, BERTScore, CodeBLEU. |
| | `benchmark.py` | `BenchmarkRunner` — dataset eval + MLflow logging; `run_spider`/`run_bird`. |
| | `mlflow_tracker.py` | `MLflowTracker` — URI normalization, run/param/metric logging. |
| `streamlit_app` | `app.py` | 4-page UI consuming core modules directly. |

## 2. Dependency Graph (import direction)

```
                         configs/default.yaml
                                  |
                          src.utils.config
                                  |
        +-------------------------+--------------------------+
        |                         |                          |
   src.models            src.text2sql.prompt_builder   src.utils.seeds
        |                         |                          |
        +-----------> src.text2sql.sql_generator <----------+
                                  |
   src.text2sql.sql_validator     |     src.text2sql.sql_executor
                 \                |                /
                  \               |               /
                   +-----> src.query_engine.engine <----- src.sql2nosql.translator
                                  |
                                  |                         src.sql2nosql.evaluator
                                  v
                            src.api.main  <----- src.api.schemas
                                  ^                  ^
                                  |                  |
                         evaluation.metrics    evaluation.benchmark
                                  ^                  |   |
                                  |                  |   +--> evaluation.mlflow_tracker
                            (used by)                |
                                  |                  +--> datasets.spider_loader / bird_loader
                          streamlit_app.app          |
                                                 datasets.preprocess (standalone)
```

Key properties:

- **No circular imports.** `evaluation.metrics` lazily imports `src.text2sql.{validator,
  executor}` inside methods (avoids load-time cycles and heavy deps).
- **Heavy deps deferred**: `torch`/`transformers` imported inside `CodeGenModel.load()` /
  `generate()`; metric libs imported inside each metric method with try/except fallbacks.
- **Config flows down** from `configs/default.yaml` via `load_config()` into generators,
  engine, benchmark, and tracker.

## 3. Service Boundaries (runtime processes)

| Service | Entry point | Port | Depends on |
|---------|-------------|------|-----------|
| REST API | `uvicorn src.api.main:app` | 8000 | core `src.*`, `evaluation.metrics`, config |
| Streamlit UI | `streamlit run streamlit_app/app.py` | 8501 | core `src.*`, `evaluation.metrics`, config |
| MLflow server | `mlflow server` (compose) / local SQLite store | 5000 | `mlruns/` volume / `mlflow.db` |

The API and UI are **independent** front ends that both import the same core library code
directly (the Streamlit UI does **not** call the API over HTTP). Docker Compose runs all
three as separate containers sharing `./data` and `./mlruns` volumes.

## 4. Data Flow

### Interactive query (`QueryEngine.process`)
```
question, schema, [db_path]
   │
   ▼
SQLGenerator.generate ── PromptBuilder.build ──> CodeGenModel.generate (HF) ──> raw text
   │                                                                  │
   │                                              _extract_sql (regex/code-fence)
   ▼
sql ──> SQLValidator.validate (sqlparse + SQLite EXPLAIN)
   │
   ├─(valid & db_path)──> SQLExecutor.execute (SQLite) ──> rows
   │
   ├──> SQLToNoSQLTranslator.translate ──> mongodb_query + warnings
   │
   ▼
_explain ──> human-readable string
   │
   ▼
{question, schema, sql, raw_model_output, validation, execution, nosql, explanation}
```

### Benchmark evaluation (`BenchmarkRunner.run_on_dataset`)
```
SpiderLoader/BirdLoader.load_split ──> standardized examples [{question, schema, sql, db_id}]
   │  (capped at config.evaluation.max_samples)
   ▼
SQLGenerator.generate_batch ──> predictions [{sql, ...}]
   │
   ▼
db_resolver(db_id) ──> per-example SQLite db_paths
   │
   ▼
EvaluationMetrics.evaluate_all(predictions, references, db_paths)
   │   ├─ exact_match (normalized sqlparse)
   │   ├─ syntax_validity (SQLValidator)
   │   ├─ execution_accuracy (SQLExecutor.compare_results)
   │   ├─ bleu / rouge_l / bertscore (with token-overlap fallback)
   │   └─ codebleu {codebleu, ngram, syntax, semantic}
   ▼
MLflowTracker.log_evaluation ──> mlflow.db (params + metrics) ──> run_id
```

### Dataset standardization
Both loaders normalize raw benchmark JSON into a common schema:
`{question, schema, sql, db_id[, difficulty]}`. Spider builds schema strings from
`tables.json` (`Table name(col type, ...)`); BIRD synthesizes schema hints from `db_id` +
`evidence`. `DatasetPreprocessor` further cleans whitespace/semicolons, splits, and
computes corpus statistics.

## 5. Cross-cutting Concerns

- **Configuration**: single YAML (`configs/default.yaml`) → `load_config()`; cached via
  `@lru_cache` in API.
- **Reproducibility**: `set_seeds()` (random/numpy/torch) called in `BenchmarkRunner` and
  scripts; seeds in config (all 42).
- **Logging**: shared `"codegen"` logger (`setup_logging`), used for warnings in loaders
  and translator.
- **Graceful degradation**: every external metric library and the model are optional at
  runtime — failures fall back to token overlap / lazy errors rather than import crashes.
- **Testability**: constructors accept injected collaborators; `tests/conftest.py`
  provides `mock_model`, `sample_db`, and `sample_examples` fixtures.
