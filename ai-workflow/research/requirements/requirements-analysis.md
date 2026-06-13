# Requirements Analysis — CodeGen Studio

## 1. Implemented Features (verified in code)

### Text-to-SQL
- [x] Prompt construction from schema + question (`PromptBuilder`, default/custom template).
- [x] CodeGen model loading with device auto-resolution (cuda/cpu) and lazy load
  (`CodeGenModel`).
- [x] Greedy and beam-search decoding (`decoding_strategy` config + per-request override).
- [x] SQL extraction from raw model output via code-fence and keyword regex
  (`SQLGenerator._extract_sql`).
- [x] Single and batch generation (`generate`, `generate_batch`).

### SQL validation & execution
- [x] Syntax validation via sqlparse + required-keyword check (`SQLValidator.validate_syntax`).
- [x] Completeness checks (balanced parens, SELECT-without-FROM, min length).
- [x] Optional SQLite `EXPLAIN`-based validation against a DB.
- [x] SQL execution on SQLite with dict rows (`SQLExecutor.execute`).
- [x] Order-independent result-set comparison (`compare_results` / `_normalize_rows`).

### SQL → NoSQL (MongoDB)
- [x] SELECT, WHERE, ORDER BY, LIMIT, GROUP BY translation.
- [x] `find()` and `aggregate()` output forms; structured filter/projection.
- [x] Comparison operators (`= != <> > < >= <=`) → Mongo operators; value casting.
- [x] AST extraction (sqlparse) with regex WHERE fallback.
- [x] Warnings for unsupported constructs (JOIN, HAVING, UNION, write statements).
- [x] Translation evaluator (exact match, token-F1, structural equivalence).

### Interactive pipeline
- [x] End-to-end `QueryEngine.process` (generate→validate→execute→translate→explain).
- [x] Human-readable explanation generation.

### Datasets
- [x] Spider loader: auto-download (GitHub repo + gdown full-data mirror fallback),
  schema build from `tables.json`, splits (train/dev/test), DB path resolution.
- [x] BIRD loader: auto-download (DAMO-ConvAI), evidence-based schema hints, splits,
  DB path resolution.
- [x] Preprocessing: cleaning, train/test split, JSON save, corpus statistics.

### Evaluation
- [x] Metrics: Exact Match, Execution Accuracy, Syntax Validity, BLEU, ROUGE-L,
  BERTScore, CodeBLEU (n-gram/syntax/semantic) — with token-overlap fallbacks.
- [x] `BenchmarkRunner` for Spider/BIRD with `max_samples` capping.
- [x] MLflow tracking (SQLite store), params + metrics, URI normalization.

### Serving & tooling
- [x] FastAPI: `/health`, `/generate-sql`, `/translate-nosql`, `/execute-query`,
  `/evaluate`, `/interactive-query` with Swagger docs.
- [x] Streamlit 4-page UI.
- [x] Scripts: `setup_sample_db`, `run_baseline_eval`, `demo_presentation`, shell launchers
  (`train.sh`, `evaluate.sh`, `run_api.sh`, `run_streamlit.sh`), PowerShell setup.
- [x] Dockerfile + docker-compose (api/streamlit/mlflow).
- [x] pytest suite (~679 lines, 10 modules) with mock model + temp DB fixtures.
- [x] Demo notebooks (`01_text2sql_demo.ipynb`, `02_evaluation_demo.ipynb`).
- [x] Reproducibility seeds (random/numpy/torch).

## 2. Missing / Placeholder Features

- [ ] **Model fine-tuning / training loop** — `scripts/train.sh` is an explicit placeholder
  ("evaluates pre-trained CodeGen-350M-Multi"; no training code exists).
- [ ] **Real MongoDB execution** — translator emits query *strings* only; no driver
  (`pymongo`) integration, no execution, no NoSQL execution-accuracy metric.
- [ ] **JOIN / HAVING / UNION / subquery** translation to MongoDB (warned, not handled).
- [ ] **Aggregate functions** in NoSQL output — GROUP BY produces only `$group._id`; no
  `$sum`/`$avg`/`$count` accumulators are emitted.
- [ ] **API auth / rate limiting / CORS** — none configured.
- [ ] **Persistent results store / dashboards** — Streamlit eval charts use hard-coded
  sample data, not live MLflow runs.
- [ ] **Batched/parallel generation** — `generate_batch` loops sequentially (no true batch
  inference through the model).
- [ ] **CI configuration** — no `.github/workflows` or other CI present.
- [ ] **`gdown` dependency** — referenced in `spider_loader` but not in `requirements.txt`.

## 3. Inferred / Implicit Requirements

- **Reproducibility** is a first-class concern (seeds, fixed config, MLflow). Any change
  should preserve deterministic behavior.
- **Offline-friendly / graceful degradation**: metric libraries and the model must be
  optional at runtime; the system should still import and run with fallbacks.
- **Small-model realism**: low exact-match is expected for a 350M base model; execution
  accuracy is positioned as the strongest metric (see demo script commentary).
- **Teaching/demo orientation**: clear, narrated scripts and notebooks suggest the code is
  meant to be read and explained, not just run.
- **Cross-platform support**: Windows (PowerShell), macOS, Linux instructions and
  cross-platform MLflow URI handling indicate multi-OS usage is required.
- **Standardized example schema** `{question, schema, sql, db_id}` is the contract between
  loaders, generator, and evaluator — must be preserved across datasets.

## 4. Constraints

- **Python 3.11** (Dockerfile, README) — type hints use `X | None` (3.10+ syntax).
- **PYTHONPATH must include project root** — imports are absolute (`src.*`, `evaluation.*`,
  `datasets.*`); scripts inject root into `sys.path`, shell scripts export PYTHONPATH.
- **Model download ~700MB** on first real run; CPU-capable but slow.
- **SQLite-only execution** — execution accuracy requires per-`db_id` `.sqlite` files
  present locally (downloaded with full Spider/BIRD data).
- **Network access** required for dataset/model downloads (Spider full data via Google
  Drive/gdown).
- **`datasets` package name collision risk** — local `datasets/` shadows the HF `datasets`
  PyPI package on `sys.path`; ordering matters.
- **License**: research/academic use; dataset and model licenses apply.

## 5. Acceptance-style Expectations (derived from tests)

- `/health` returns `{status: "healthy", version}`.
- `/translate-nosql` returns `success=True` and a `mongodb_query` for a simple SELECT.
- `/execute-query` returns correct `row_count` against a SQLite DB.
- `/evaluate` returns a metrics dict including `exact_match` and `bleu`; mismatched
  prediction/reference lengths → HTTP 400.
- Translator handles WHERE/ORDER BY/LIMIT/GROUP BY for SELECT statements.
- Metrics return floats in `[0, 1]` and degrade to token overlap without optional libs.
