# Risk Analysis — CodeGen Studio

Severity legend: **High** (security/correctness/blocking), **Medium** (reliability/perf),
**Low** (maintainability/polish).

## 1. Security Risks

### [High] Arbitrary SQL execution via `/execute-query`
`SQLExecutor.execute` runs any SQL string the caller provides, against any `db_path` the
caller provides. The `/execute-query` endpoint exposes this with no auth, no allow-list,
and no sandboxing. A caller can run destructive DML/DDL or read arbitrary SQLite files on
the host.
- **Files**: `src/api/main.py` (`execute_query`), `src/text2sql/sql_executor.py`.
- **Mitigation**: restrict to SELECT, validate/whitelist `db_path` under a data root, run
  read-only connections (`mode=ro`), add auth, set query timeouts.

### [High] Arbitrary file path disclosure via `db_path`
Both `/execute-query` and `/interactive-query` accept caller-supplied filesystem paths,
allowing probing/reading of any `.sqlite`/`.db` file the server process can access.
- **Mitigation**: resolve and confine paths to a configured data directory; reject
  absolute/`..` paths.

### [Medium] No API hardening
No authentication, CORS policy, rate limiting, or request-size limits. Large prompts could
drive memory/CPU exhaustion (model + BERTScore downloads).
- **Mitigation**: add API key/auth, CORS config, body-size and concurrency limits.

### [Low] EXPLAIN via f-string
`SQLValidator.validate_with_sqlite` builds `EXPLAIN {sql}` by string interpolation. It is
`EXPLAIN`-only (no execution) but still unsanitized; combined with the executor it
reinforces the injection surface.

## 2. Correctness / Functional Risks

### [High] Per-request model reload in `/interactive-query`
`interactive_query` constructs a **new** `QueryEngine` on every call, which builds a new
`SQLGenerator` → new `CodeGenModel`. The first `generate()` then reloads the ~700MB model
from scratch per request (the `lru_cache` singletons used by other endpoints are bypassed).
- **Files**: `src/api/main.py` (`interactive_query`), `src/query_engine/engine.py`.
- **Impact**: severe latency/memory churn under any real use.
- **Mitigation**: cache a singleton `QueryEngine` (e.g. `@lru_cache`) like the other deps.

### [High] `SpiderLoader._download_spider_data` can raise `NameError`
In the nested-folder copy branch, `import shutil` only runs `if dest.exists()`, but
`shutil.copytree(...)` is called unconditionally afterward. When `item.is_dir()` and the
destination does **not** exist, `shutil` is undefined → `NameError`.
- **File**: `datasets/spider_loader.py` (~lines 86–96).
- **Mitigation**: move `import shutil` to module top.

### [Medium] `gdown` referenced but not declared
`spider_loader` imports `gdown` for the full Spider data mirror; it is **not** in
`requirements.txt`. The `requests` fallback hits a Google Drive URL that returns an HTML
confirmation page, not the zip → corrupt/failed extraction.
- **Mitigation**: add `gdown` to requirements or document a manual data path.

### [Medium] `datasets/` shadows the HuggingFace `datasets` package
`requirements.txt` pins `datasets>=2.16.0`, but the local top-level `datasets/` package
shadows it on `sys.path`. Any code doing `from datasets import load_dataset` would import
the local package instead.
- **Mitigation**: rename local package (e.g. `data_loaders/`) or drop the unused HF dep.

### [Medium] SQL extraction collapses multi-line SQL
`SQLGenerator._extract_sql` returns the first SQL-like *line* when no code fence is present,
truncating multi-line generated queries.
- **Mitigation**: capture from the first SQL keyword to statement terminator/end.

### [Medium] NoSQL translator coverage gaps
- WHERE regex fallback only splits on `AND` (no `OR`, `IN`, `LIKE`, `BETWEEN`).
- GROUP BY emits only `$group._id` — no aggregation accumulators (`$sum`, `$avg`, count).
- JOIN/HAVING/UNION/subqueries are warned but unsupported.
- Comparison parsing in `_parse_comparison` is heuristic and can mis-assign left/right.
- **Mitigation**: document scope clearly (already partly warned) and/or extend rules.

### [Medium] Inconsistent MLflow tracking stores
Config uses `sqlite:///mlflow.db`; `demo_presentation.py` passes a **directory**
(`ROOT/'mlruns'`); docker-compose's MLflow server uses a `/mlruns` file store. These three
can produce **separate, non-mergeable** experiment histories.
- **Mitigation**: standardize on one backend store URI across config/scripts/compose.

### [Low] `GenerateSQLRequest.schema` shadows Pydantic
Naming a field `schema` shadows `BaseModel.schema()` and triggers Pydantic warnings; could
break tooling that calls `.schema()`.
- **Mitigation**: rename to `db_schema` with an alias for backward-compatible JSON.

### [Low] `/interactive-query` uses raw params, not a request model
Unlike the other POST endpoints, it declares `question`, `schema`, `db_path` as function
args → FastAPI treats them as **query** params, inconsistent with the JSON-body endpoints.
- **Mitigation**: introduce an `InteractiveQueryRequest` Pydantic model.

## 3. Performance / Scalability Risks

- **[Medium] No true batch inference** — `generate_batch` loops example-by-example; benchmarks
  on Spider/BIRD will be slow.
- **[Medium] No execution timeouts** — long/heavy SQL can hang the executor and the API
  worker.
- **[Medium] BERTScore/CodeBLEU heavy** — first call downloads models; per-call cost is
  high and silently falls back to token overlap on failure (metrics can become inconsistent
  across environments without notice).
- **[Low] Single-process serving** — no worker/concurrency guidance; model is not
  thread-safe under concurrent requests.

## 4. Tech Debt / Maintainability

- **[Medium] No CI** — no automated quality gate for linting or regression checks.
- **[Medium] No dedicated regression suite** — real-model and full-download integration
  regressions can go uncaught.
- **[Low] Hard-coded sample data in Streamlit eval charts** — the "Evaluation Dashboard"
  shows fabricated numbers rather than live MLflow runs; misleading in demos.
- **[Low] Duplicated reference example sets** — `run_baseline_eval.py` and
  `demo_presentation.py` each define their own near-identical benchmark examples.
- **[Low] `__init__.py` exports minimal** — most packages expose nothing; consumers rely on
  deep imports.

## 5. Operational Risks

- **[Medium] Network dependency** — first run downloads model + datasets; offline/airgapped
  environments need pre-staged caches.
- **[Low] `.gitignore` excludes `*.db`/`*.sqlite`/`mlruns/`** — sample DB and MLflow runs are
  regenerated, not versioned (intended, but means clean clones have no results until
  scripts run; Dockerfile mitigates by running `setup_sample_db.py` at build).
- **[Low] Cross-platform path handling** — mostly handled (Pathlib, URI normalization), but
  PowerShell instructions hard-code a user-specific path in the README.
