# Feature Plan — AI SQL Assistant (Streamlit UI)

> **Feature:** `text2sql-ui-tool`  
> **Date:** 2026-07-16  
> **Spec:** `tool/docs/AI_Text_to_SQL_UI_Specification.md` (v1.1)  
> **Status:** PENDING APPROVAL (see `approvals/text2sql-ui-tool-approval.md`)

---

## 1. Problem

The repo has a mature Text-to-SQL inference stack (`src/text2sql/`, `src/models/`) and
evaluation tooling, but **no user-facing application** for interactive NL→SQL against a
live PostgreSQL database. The `tool/` directory is documentation-only.

Developers and demo users need a lightweight Streamlit app that:

- Accepts natural language, generates SQL with the fine-tuned LoRA adapter, validates,
  and executes in one **Execute** action
- Shows **structured activity logs** for every pipeline stage
- Displays results in a **scrollable, view-only** table (no charts or downloads)
- Is **extensible** via tabs for future SQL-to-NoSQL and documentation

---

## 2. Goal

Deliver a working **Text-to-SQL tab** under `tool/` that:

- Connects to PostgreSQL, introspects schema, and **selects relevant tables from the user prompt**
- Builds prompts locally and calls the **FastAPI-deployed LoRA adapter** (no direct model access from the tool)
- Validates and executes read-only SQL, with structured logging and Streamlit UI entirely under `tool/`

---

## 3. Scope

### In scope (MVP — v1.0)

| Item | Detail |
|------|--------|
| Location | All new application code under `tool/` |
| UI framework | Streamlit tab shell + shared activity panel |
| Primary tab | **Text-to-SQL** — full NL→SQL→validate→execute workflow |
| Execute action | Single button (no separate Generate); Ctrl/Cmd+Enter shortcut |
| Database | PostgreSQL via SQLAlchemy (`psycopg` driver) |
| Schema introspection | Live PG introspection → per-table metadata + DDL |
| **Schema selection** | **Prompt-based** — retrieve relevant tables from user question before inference |
| Inference | **FastAPI only** — LoRA adapter deployed in `hf-deploy`; tool has **no direct model/adapter access** |
| Prompt building | Local `PromptBuilder` with **retrieved schema subset** only |
| SQL extraction | Reuse patterns from `src/text2sql/sql_generator.py` (post-API response) |
| Validation | Reuse `SQLValidator` + **read-only safety gate** (SELECT/WITH only) |
| Execution | Read-only SQL against connected PostgreSQL; row limit configurable |
| Activity log | Structured events (`timestamp`, `level`, `stage`, `event`, `message`, `details`) |
| Results | Scrollable `st.dataframe` in fixed-height container; row count + duration |
| **Settings page** | Database connections + **FastAPI endpoint** config (no local model settings) |
| **Connection tests** | Test Database and Test API buttons with latency + structured result |
| Stub tabs | SQL-to-NoSQL and Documentation tabs (placeholder UI, adapter interface ready) |
| Config | `tool/.env.example`, `tool/config.yaml`, persisted `tool/.local/settings.json` (gitignored) |
| Tests | Unit tests for schema selector, validator, settings, connection tester, pipeline |

### Out of scope (initial release)

| Item | Notes |
|------|-------|
| SQL-to-NoSQL full implementation | Stub tab + adapter interface only |
| Documentation tab content | Placeholder; wire in later |
| Charts / Plotly | Spec explicitly excludes |
| Result or SQL file downloads | View-only results; optional Copy SQL only |
| Local model / LoRA loading in tool | LoRA lives in FastAPI deployment only |
| Direct `src.models.model_loader` usage | Tool calls HTTP API; no torch/peft in tool runtime |
| Authentication / RBAC | Future |
| Query history / conversation memory | Future |
| VS Code extension | Separate product (`tool/docs/requirements.md`) |

---

## 4. Architecture Decisions

### AD-1 — All application code lives under `tool/`

```
tool/
├── app.py                         # Streamlit entry + navigation (Home / Settings)
├── config.py                      # ToolConfig dataclass + env/yaml loading
├── requirements.txt               # streamlit, sqlalchemy, httpx, sentence-transformers, sqlparse, pandas
├── .env.example
├── .gitignore                     # .local/
├── README.md
│
├── pages/
│   └── settings.py                # Settings page (DB connections + FastAPI)
│
├── core/
│   ├── activity_logger.py         # Structured event buffer + emit API
│   ├── settings_store.py          # Load/save connections + FastAPI config to .local/
│   ├── connection_tester.py       # test_database(), test_fastapi()
│   ├── database.py                # SQLAlchemy engine from saved connection
│   ├── schema_loader.py           # PG introspection → per-table TableSchema
│   ├── schema_selector.py         # Prompt-based relevant table retrieval (embeddings)
│   ├── safety_validator.py        # Read-only SQL gate (SELECT, WITH only)
│   ├── executor.py                # PG read-only execution → pandas DataFrame
│   └── inference/
│       ├── base.py                # InferenceClient protocol
│       └── fastapi_client.py      # OpenAI-compatible client → hf-deploy API (only backend)
│
├── pipeline/
│   └── text2sql_pipeline.py       # Orchestrates Execute workflow end-to-end
│
├── adapters/
│   ├── base.py                    # QueryAdapter protocol
│   ├── text2sql_adapter.py        # NL in → SQL out → execute
│   └── sql2nosql_adapter.py       # Stub (NotImplemented / coming soon)
│
├── ui/
│   ├── shell.py                   # Page config, header, connection badge, tab routing
│   ├── activity_panel.py          # Structured log renderer (auto-scroll)
│   ├── query_panel.py             # NL textarea + Execute/Clear
│   ├── sql_panel.py               # Read-only SQL + validation badge + copy
│   ├── output_panel.py            # Scrollable dataframe + metadata
│   └── tabs/
│       ├── text2sql_tab.py
│       ├── sql2nosql_tab.py       # Stub
│       └── docs_tab.py            # Stub
│
└── tests/
    ├── test_activity_logger.py
    ├── test_settings_store.py
    ├── test_connection_tester.py
    ├── test_safety_validator.py
    ├── test_schema_loader.py
    ├── test_schema_selector.py
    ├── test_fastapi_client.py
    ├── test_executor.py
    └── test_text2sql_pipeline.py
```

**Run from repo root** so `src/` imports resolve:

```bash
cd /Volumes/Work/CodeGen-Implementations-May_26
streamlit run tool/app.py
```

Add repo root to `sys.path` in `tool/app.py` if needed (same pattern as scripts).

### AD-2 — Reuse `src/` for prompts and validation only; inference via FastAPI

| Concern | Reuse from `src/` | New in `tool/` |
|---------|-------------------|----------------|
| **Inference / LoRA** | — (not in tool) | `core/inference/fastapi_client.py` → `hf-deploy` API |
| Prompt template | `src.text2sql.prompt_builder.PromptBuilder` | Built locally with **selected schema** |
| SQL extraction | `src.text2sql.sql_generator` extraction patterns | Post-API response parsing |
| Syntax validation | `src.text2sql.sql_validator.SQLValidator` | `core/safety_validator.py` adds read-only gate |
| Schema introspection | — | `core/schema_loader.py` |
| **Schema selection** | — | `core/schema_selector.py` (embedding retrieval) |
| PG execution | — | `core/executor.py` via SQLAlchemy |
| Activity logging | — | `core/activity_logger.py` |
| Saved connections | — | `core/settings_store.py` |
| Connection testing | — | `core/connection_tester.py` |

**Important:** The tool does **not** import `src.models.model_loader` or load torch/peft adapters. All Text-to-SQL generation goes through the deployed FastAPI service where the LoRA adapter is mounted.

### AD-3 — Adapter protocol for tab extensibility

```python
# tool/adapters/base.py
class QueryAdapter(Protocol):
    name: str
    def execute(self, user_input: str, *, logger: ActivityLogger, db: DatabaseSession) -> ExecuteResult: ...
```

- **Text2SQLAdapter** — implements full MVP workflow
- **Sql2NoSqlAdapter** — stub raises or shows "Coming soon"; same interface for future wiring to `src/sql2nosql/`

Tabs register adapters; shell renders shared panels. Adding a tab = new adapter + thin tab module.

### AD-4 — Single Execute pipeline (no partial generate)

`Text2SqlPipeline.run(question)` executes stages sequentially; each stage emits structured logs.
On failure at any stage, pipeline stops and returns error state (no execution).

```
connect → load_all_tables → select_tables_for_prompt(question) → build_schema_ddl(selected)
  → build_prompt → fastapi_inference → extract_sql → safety_validate → execute → build_result
```

UI updates SQL panel after `extract_sql` (via `st.session_state`) before execution completes.

### AD-5 — PostgreSQL schema introspection + prompt-based selection

#### Step 1 — Introspect all tables (`schema_loader.py`)

Via SQLAlchemy `Inspector`:

- List tables in configured schema (default `public`)
- For each table: columns, types, PK, FK references
- Build `TableSchema` with name, DDL snippet, column names, FK links

#### Step 2 — Select relevant tables (`schema_selector.py`)

Given the **user's natural language prompt**, retrieve the subset of tables to include in the model prompt.

| Aspect | Detail |
|--------|--------|
| Method | **Embedding similarity** (primary) — align with VS Code extension approach |
| Model | `BAAI/bge-small-en-v1.5` (default) or `all-MiniLM-L6-v2` via `sentence-transformers` |
| Index unit | One embedding per **table** (table name + column names + optional DDL summary) |
| Query | Embed user question; cosine similarity against all table embeddings |
| Top-K | Configurable `SCHEMA_TOP_K` (default **8**) |
| Min score | `SCHEMA_MIN_SCORE` threshold; fall back if none pass |
| FK expansion | After top-K, include tables referenced by FK from selected set |
| Fallback | If DB has ≤ `SCHEMA_TOP_K` tables, include all; log `method: "full_schema"` |

**Structured log event:**

```python
logger.info(
    stage="schema",
    event="tables_selected",
    message="Selected relevant tables for prompt",
    details={
        "method": "embedding",
        "selected": ["Customers", "Orders"],
        "scores": {"Customers": 0.82, "Orders": 0.71},
        "top_k": 8,
        "total_tables": 24,
    },
)
```

#### Step 3 — Build prompt DDL

Concatenate DDL for **selected tables only** → `PromptBuilder.build(question, schema)`.

This keeps prompts within model context and improves SQL quality vs sending the full database schema.

### AD-6 — Read-only safety validator (separate from syntax)

Before execution, parse with `sqlparse` and reject any statement type other than `SELECT` or `WITH`.
Block: INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, and multi-statement batches.

Log validation events:

```python
logger.warning(stage="validation", event="validation_failed",
               message="Blocked non-SELECT statement", details={"reason": "DELETE detected"})
```

### AD-7 — Streamlit session state contract

| Key | Type | Purpose |
|-----|------|---------|
| `activity_events` | `list[ActivityEvent]` | Structured log buffer |
| `generated_sql` | `str \| None` | Last generated SQL |
| `validation_status` | `dict \| None` | Pass/fail + message |
| `result_df` | `pd.DataFrame \| None` | Query results |
| `result_meta` | `dict` | row_count, duration_ms, truncated |
| `db_connected` | `bool` | Connection status for header (from active saved connection) |
| `selected_tables` | `list[str]` | Tables chosen by schema selector for last Execute |
| `settings_loaded` | `bool` | Settings store initialized |

Clear button resets query-related keys; optionally clears activity log (configurable, default: clear log).

### AD-8 — Inference: FastAPI only (LoRA not accessible from tool)

The fine-tuned LoRA adapter is **deployed in the FastAPI service** (`hf-deploy`). The Streamlit tool is a **thin client** — it builds the prompt locally (with retrieved schema) and sends it to the API. It never loads CodeGen, peft, or adapter weights.

**FastAPI settings fields** (Settings page):

| Field | Default | Notes |
|-------|---------|-------|
| `base_url` | `http://localhost:8000/v1` | OpenAI-compatible base (append `/chat/completions`) |
| `health_url` | `http://localhost:8000/health` | Derived from base or explicit |
| `api_key` | empty | Optional; sent as `Authorization: Bearer` |
| `model` | `codegen-text2sql` | Or `codegen-multi-adapter` |
| `intent` | `text2sql` | Passed as `intent` override on request body |
| `timeout_sec` | 60 | HTTP timeout for inference |
| `max_tokens` | 256 | Maps to `max_tokens` on chat completion |

**FastAPI request** (matches `hf-deploy/hf_deploy/api/schemas.py`):

```python
POST {base_url}/chat/completions
{
  "model": "codegen-text2sql",
  "intent": "text2sql",
  "messages": [{"role": "user", "content": "<full prompt with schema>"}],
  "temperature": 0.2,
  "max_tokens": 256
}
```

Response: extract `choices[0].message.content`, then apply SQL extraction (reuse `SQLGenerator` parsing logic without loading the model).

**Test API** action:
1. `GET /health` → expect `{"status": "ok", "router": {...}}`
2. Optionally `GET /v1/models` to list available models
3. Display latency, router status (adapters loaded, checkpoint version), success/fail banner

Reference: `hf-deploy/hf_deploy/api/app.py`, `hf-deploy/README.md`

### AD-9 — Settings page (database connections + FastAPI)

Dedicated Streamlit **Settings** page (`tool/pages/settings.py`), linked from sidebar navigation — not crammed into the main workspace sidebar.

#### Section A — Database connections

- **Add / edit / delete** named PostgreSQL connections
- **Fields per connection:** name, host, port, database, username, password, schema (default `public`), SSL mode
- **Active connection** dropdown (used by Text-to-SQL tab header badge)
- **Test Connection** button per connection and for the active connection
- Persist to `tool/.local/settings.json` (gitignored); seed from `DATABASE_URL` in `.env` on first run if present

**Test Database** behavior (`connection_tester.test_database(conn)`):
- Open SQLAlchemy engine with 5s connect timeout
- Run `SELECT 1 AS ok`
- Optional: fetch `SELECT version()` for display
- Return `{success, latency_ms, server_version?, error?}`
- Emit structured log event: `connection_test_passed` | `connection_test_failed`

#### Section B — FastAPI (inference endpoint)

- Base URL, API key, model, intent (`text2sql`), timeout
- Read-only note: LoRA adapter runs on this server, not in the tool
- **Test API** button → health check + router status JSON
- Save applies to settings store; Execute uses saved endpoint

#### Section C — Schema selection

- Embedding model name (default `BAAI/bge-small-en-v1.5`)
- `SCHEMA_TOP_K` (default 8)
- `SCHEMA_MIN_SCORE` (default 0.3)

#### Section D — Execution limits (optional collapsible)

- `MAX_RESULT_ROWS`, `QUERY_TIMEOUT_SEC`, `SCHEMA_MAX_TABLES`

**Settings store schema** (simplified):

```json
{
  "active_connection_id": "conn-1",
  "connections": [
    {
      "id": "conn-1",
      "name": "Local PostgreSQL",
      "host": "localhost",
      "port": 5432,
      "database": "mydb",
      "username": "postgres",
      "password": "***",
      "schema": "public",
      "ssl_mode": "prefer"
    }
  ],
  "fastapi": {
    "base_url": "http://localhost:8000/v1",
    "api_key": "",
    "model": "codegen-text2sql",
    "intent": "text2sql",
    "timeout_sec": 60
  },
  "schema_selection": {
    "embedding_model": "BAAI/bge-small-en-v1.5",
    "top_k": 8,
    "min_score": 0.3
  }
}
```

Passwords stored in gitignored local file only — document security note in README.

### AD-10 — Execution limits

| Setting | Default | Purpose |
|---------|---------|---------|
| `MAX_RESULT_ROWS` | 1000 | Cap rows returned; set `truncated: true` in log |
| `QUERY_TIMEOUT_SEC` | 30 | SQLAlchemy execution timeout |
| `SCHEMA_TOP_K` | 8 | Max tables sent to model after retrieval |
| `SCHEMA_MIN_SCORE` | 0.3 | Minimum embedding similarity to include a table |

---

## 5. Execution Stages

| Stage | Name | Deliverable | Depends on |
|-------|------|-------------|------------|
| 0 | Scaffold | `tool/` layout, deps, config, README, stub app + Settings page | — |
| 1 | Core services | activity logger, settings store, connection tester, DB, schema loader, **schema selector**, validator, executor | 0 |
| 2 | Inference + pipeline | FastAPI client, text2sql adapter + pipeline (with schema selection) | 1 |
| 3 | UI shell | tabs, panels, Settings page, Execute/Clear wiring | 1, 2 |
| 4 | Polish & tests | scrollable output, connection test UX, unit tests, error UX | 3 |
| 5 | Stub extensibility | sql2nosql + docs tab placeholders, adapter registry | 3 |

Stages 0–4 = MVP. Stage 5 = same sprint or immediately after MVP.

---

## 6. Assumptions

1. PostgreSQL is reachable from the machine running Streamlit (local or network).
2. **LoRA adapter is deployed in the FastAPI service** (`hf-deploy`) — the tool does **not** load adapters or base models directly.
3. FastAPI endpoint is reachable from the tool (localhost, internal network, or HF Space URL).
4. User runs the app from repo root with Python 3.10+; **`tool/requirements.txt` only** (no repo `torch`/`peft` required for the Streamlit app).
5. **Schema selection runs locally** in the tool via `sentence-transformers` (lightweight); only the final prompt + selected schema subset is sent to FastAPI.
6. Streamlit reruns on button click are acceptable; pipeline completes in one rerun (no background threads for MVP).

---

## 7. Open Questions

| # | Question | Resolution |
|---|----------|------------|
| OQ-1 | Connection string source: sidebar vs Settings page? | **Settings page** + `.env` seed on first run |
| OQ-2 | Table selection method? | **Embedding retrieval** on table metadata; FK expansion; top-K config |
| OQ-3 | What if FastAPI is down? | Block Execute; Test API on Settings; clear error in activity log |
| OQ-4 | Clear button clears activity log? | Yes (per spec "optionally clears") |
| OQ-5 | Local model fallback? | **No** — FastAPI is the only inference path |

---

## 8. Success Criteria (from spec)

- [ ] **Settings page** manages DB connections and FastAPI inference config
- [ ] **Test Connection** and **Test API** work with clear success/fail feedback
- [ ] Inference goes **only through FastAPI** (no local LoRA loading)
- [ ] **Schema selection** picks relevant tables from user prompt before inference
- [ ] Selected tables visible in structured activity log (`tables_selected` event)
- [ ] Single **Execute** generates, validates, and runs SQL
- [ ] Generated SQL visible on same screen
- [ ] Only validated read-only SQL executes
- [ ] Scrollable, view-only result table
- [ ] Structured activity log with maximal observable events
- [ ] Tab shell ready for SQL-to-NoSQL without rework
- [ ] No charts; no result downloads
- [ ] All code under `tool/` (imports from `src/` allowed)

---

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Wrong tables selected | Incorrect SQL | Log scores; FK expansion; tune top-K; future: hybrid keyword boost |
| FastAPI server down | Cannot generate SQL | Test API on Settings page; clear error on Execute |
| Embedding model download | First-run delay | Cache model; log `embedding_model_loaded` event |
| Passwords in local settings file | Security risk | Gitignore `.local/`; document; no commit of secrets |
| Streamlit rerun loses in-flight state | Confusing UX | Single synchronous pipeline per Execute |
| PG DDL introspection ≠ training format | Model confusion | Match Spider-style CREATE TABLE format; test against known DB |
| GPU memory on shared machine | OOM in FastAPI server | Document; FastAPI runs separately from tool |

---

## 10. References

- UI spec: `tool/docs/AI_Text_to_SQL_UI_Specification.md`
- FastAPI deploy: `hf-deploy/hf_deploy/api/app.py`
- FastAPI README: `hf-deploy/README.md`
- API schemas: `hf-deploy/hf_deploy/api/schemas.py`
- VS Code schema retrieval pattern: `tool/docs/requirements.md` (Section 8–10)
- Embedding eval helper: `src/evaluation/embedding_similarity.py` (reference only)
- Prompt builder: `src/text2sql/prompt_builder.py`
- SQL extraction patterns: `src/text2sql/sql_generator.py`
