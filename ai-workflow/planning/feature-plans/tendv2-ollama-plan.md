# Feature Plan — TENDv2 (Ollama-powered dataset generation & validation)

> **Feature:** `tendv2-ollama`
> **Date:** 2026-06-24
> **Status:** APPROVED (see `approvals/tendv2-ollama-approval.md`)

---

## 1. Scope

Create a second version of the TEND pipeline (`TENDv2/`) that mirrors `TENDv1/`
but performs **MongoDB conversion, documentation generation, and evaluation via
local Ollama models** instead of in-process HuggingFace models and the
rule-based `sql-mongo-converter`.

### Model roles

| Role | Model | Responsibility |
|------|-------|----------------|
| Code generator | `qwen2.5-coder:3b` | Generate Mongo schema, Mongo query, and query documentation |
| Judge | `qwen3:4b` | Evaluate semantic equivalence (true/false) + summary |

### Output CSV columns (required)

| Column | Description | Producer |
|--------|-------------|----------|
| `question` | NLP / raw text | dataset |
| `sql_schema` | SQL DDL | rule-based (`schema_to_sql`) |
| `sql_query` | gold SQL | dataset |
| `nosql_schema` | MongoDB schema | code generator |
| `nosql_query` | MongoDB query | code generator |
| `documentation` | plain-English explanation | code generator |
| `evaluation_result` | true/false | judge |
| `evaluation_summary` | short explanation | judge |
| `metadata` | source, db_id, split, models, timings | pipeline |

### Datasets

Spider and BIRD, each with train/test (dev) splits. **Spider first**, then BIRD.

---

## 2. Architecture Decisions

- **AD-1 — Separate Ollama util.** A reusable async+sync client lives at
  `src/llm/ollama_client.py` (not scoped to TENDv2) so other modules can reuse it.
  Talks to `POST {OLLAMA_BASE_URL}/api/chat` with `stream: false`.
- **AD-2 — Async pipeline.** Code generation and judging run concurrently via
  `asyncio` with a bounded semaphore (`--concurrency`, default 8) to maximize
  throughput on large datasets while not overwhelming Ollama.
- **AD-3 — Combined codegen call with fallback.** One JSON request returns
  `nosql_schema` + `nosql_query` + `documentation` to minimize round-trips.
  If the combined JSON fails to parse or any required field is empty/invalid,
  fall back to **separate per-field calls** so accuracy is not sacrificed.
- **AD-4 — JSON-mode outputs.** Use Ollama `"format": "json"` for codegen and
  judge calls to make parsing reliable.
- **AD-5 — Disable thinking on judge.** `qwen3:4b` is a reasoning model; send
  `"think": false` and strip any `<think>…</think>` defensively to keep output
  clean and fast.
- **AD-6 — Incremental ordered CSV writes.** Rows are written as results
  complete (in input order) so very large runs preserve partial progress and
  bounded memory.
- **AD-7 — Reuse v1 deterministic pieces.** SQL DDL generation
  (`schema_to_sql`) and structural validation (`validator`) are reused; the
  rule-based `sql-mongo-converter` is **not** used for conversion (the codegen
  model owns conversion now).
- **AD-8 — Config via env.** `OLLAMA_BASE_URL`, `OLLAMA_CODEGEN_MODEL`,
  `OLLAMA_JUDGE_MODEL`, `OLLAMA_CONCURRENCY`, `OLLAMA_TIMEOUT`.

---

## 3. Module Layout

```
src/llm/
  __init__.py
  ollama_client.py        # AD-1: async + sync chat client, JSON mode, retries

TENDv2/
  __init__.py
  README.md
  prompts.py              # codegen + judge prompt templates
  code_generator.py       # qwen2.5-coder:3b -> nosql_schema/query/documentation
  judge.py                # qwen3:4b -> evaluation_result + summary
  spider_source.py        # read Spider splits (reuse v1 pattern)
  bird_source.py          # wrap BirdLoader (Stage 2)
  schema_to_sql.py        # thin re-export of TENDv1 generator
  validator.py            # structural checks (reuse)
  paths.py                # data/TENDv2 outputs, timestamped names
  build_tend_dataset.py   # async orchestrator + incremental CSV writer
  run_tend.py             # CLI entry point
```

---

## 4. Execution Stages

| Stage | Goal | Key outputs |
|-------|------|-------------|
| S1 | Ollama client util | `src/llm/ollama_client.py` (sync + async) |
| S2 | Prompts + codegen + judge | `prompts.py`, `code_generator.py`, `judge.py` |
| S3 | Sources + paths + reuse | `spider_source.py`, `paths.py`, `schema_to_sql.py`, `validator.py` |
| S4 | Async pipeline + CLI | `build_tend_dataset.py`, `run_tend.py`, `__init__.py`, `README.md` |
| S5 | BIRD support | `bird_source.py`, CLI `--dataset bird` |
| S6 | Deps + docs + smoke | `requirements.txt`, `.env.example`, import/CLI smoke |

---

## 5. Assumptions

- Ollama runs locally at `http://localhost:11434` with `qwen2.5-coder:3b` and
  `qwen3:4b` pulled.
- Spider data already cached under `data/spider` (via `SpiderLoader`); BIRD via
  `BirdLoader`.
- `httpx` is added for async HTTP.
- Outputs go to `data/TENDv2/` and do not interfere with `data/TEND/` (v1).

---

## 6. Out of Scope (this pass)

- Execution-based equivalence (running queries against real Mongo/SQLite).
- Fine-tuning / training integration.
- Streaming responses (we use `stream: false`).
