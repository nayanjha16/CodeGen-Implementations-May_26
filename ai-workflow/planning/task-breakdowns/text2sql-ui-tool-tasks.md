# Task Breakdown — AI SQL Assistant (Streamlit UI)

> **Feature:** `text2sql-ui-tool`  
> **Plan:** `feature-plans/text2sql-ui-tool-plan.md`

Complexity: **S** (< 2h), **M** (2–6h), **L** (6–16h), **XL** (> 16h)

---

## Stage 0 — Scaffold

| ID | Task | Complexity | Depends | Acceptance |
|----|------|------------|---------|------------|
| T0.1 | Create `tool/` directory structure per AD-1 | S | — | All folders exist |
| T0.2 | Add `tool/requirements.txt` (streamlit, sqlalchemy, psycopg[binary], httpx, sentence-transformers, pandas, sqlparse, pyyaml, python-dotenv) — **no torch/peft** | S | T0.1 | Tool installs without ML stack |
| T0.3 | Add `tool/.env.example` (DATABASE_URL, FASTAPI_BASE_URL, MODEL_ADAPTER_RUN, etc.) | S | T0.1 | Documented vars match plan |
| T0.4 | Add `tool/config.yaml` + `tool/config.py` (ToolConfig dataclass) | M | T0.1 | Config loads env + yaml |
| T0.5 | Add `tool/.gitignore` (`.local/`) + `tool/README.md` | S | T0.2 | Settings path documented |
| T0.6 | Stub `tool/app.py` + `tool/pages/settings.py` — navigation, empty home tabs | S | T0.1 | App launches; Settings page reachable |

---

## Stage 1 — Core Services

| ID | Task | Complexity | Depends | Acceptance |
|----|------|------------|---------|------------|
| T1.1 | Implement `ActivityEvent` dataclass + `ActivityLogger` | M | T0.4 | Unit test: events have all required fields |
| T1.2 | Implement `core/settings_store.py` — load/save connections + inference config to `.local/settings.json` | M | T0.4 | Seed from DATABASE_URL; round-trip test |
| T1.3 | Implement `core/connection_tester.py` — `test_database()`, `test_fastapi()` with latency | M | T1.2 | Returns structured TestResult |
| T1.4 | Implement `core/database.py` — engine from saved connection, `get_active_engine()` | M | T1.2 | Uses active connection from settings |
| T1.5 | Implement `core/schema_loader.py` — introspect all tables → `TableSchema` list | L | T1.4 | Per-table DDL + FK metadata |
| T1.6 | Implement `core/schema_selector.py` — embed user prompt, rank tables, top-K + FK expansion | L | T1.5 | Tests with fixed embeddings / mocks |
| T1.7 | Implement `core/safety_validator.py` — SELECT/WITH only | M | — | Tests for blocked keywords |
| T1.8 | Implement `core/executor.py` — read-only SQL → DataFrame | M | T1.4, T1.7 | Respects MAX_RESULT_ROWS |

---

## Stage 2 — FastAPI Inference & Pipeline

| ID | Task | Complexity | Depends | Acceptance |
|----|------|------------|---------|------------|
| T2.1 | Implement `core/inference/base.py` — `InferenceClient` protocol | S | T0.4 | Single backend: FastAPI |
| T2.2 | Implement `core/inference/fastapi_client.py` — POST `/v1/chat/completions`, extract SQL | M | T1.3 | Works against hf-deploy API |
| T2.3 | Implement SQL extraction helper (reuse `SQLGenerator` parsing logic, no model load) | M | — | Parses API response text |
| T2.4 | Define `adapters/base.py` — `QueryAdapter`, `ExecuteResult` | S | T1.1 | Interface documented |
| T2.5 | Implement `adapters/text2sql_adapter.py` — schema select → prompt → FastAPI → validate → execute | L | T1.*, T2.1–T2.3 | End-to-end with mocked API |
| T2.6 | Implement `pipeline/text2sql_pipeline.py` — orchestrate stages + logging | L | T2.5 | All spec events emitted |
| T2.7 | Stub `adapters/sql2nosql_adapter.py` | S | T2.4 | Tab can import without crash |

### Required pipeline log events (T2.6)

- `connection` / `connection_established` | `connection_failed`
- `settings` / `connection_test_passed` | `connection_test_failed` (Settings page)
- `inference` / `inference_mode_selected` (local | fastapi)
- `inference` / `api_test_passed` | `api_test_failed` (Settings page)
- `schema` / `schema_load_start` | `schema_loaded` (all tables count)
- `schema` / `schema_selection_start` | `tables_selected` (method, scores, selected names)
- `schema` / `fk_tables_expanded` (optional, when FK adds tables)
- `prompt` / `prompt_built`
- `inference` / `fastapi_request_start` | `sql_generated`
- `validation` / `validation_start` | `validation_passed` | `validation_failed`
- `execution` / `executing` | `rows_retrieved`
- `render` / `render_start` | `render_complete`

---

## Stage 3 — UI Shell & Panels

| ID | Task | Complexity | Depends | Acceptance |
|----|------|------------|---------|------------|
| T3.1 | Implement `ui/shell.py` — wide layout, header with active connection name + status badge | M | T0.6 | Badge reflects settings active connection |
| T3.2 | Implement `ui/activity_panel.py` — structured log renderer | M | T1.1 | Readable with 20+ events |
| T3.3 | Implement `ui/query_panel.py` — textarea, Execute, Clear | M | T3.1 | Clear resets session state |
| T3.4 | Implement `ui/sql_panel.py` — read-only SQL, validation badge, copy | M | T3.1 | SQL + pass/fail shown |
| T3.5 | Implement `ui/output_panel.py` — scrollable dataframe, metadata | M | T3.1 | No download buttons |
| T3.6 | Implement `ui/tabs/text2sql_tab.py` — compose panels + wire Execute | L | T2.6, T3.2–T3.5 | End-to-end demo works |
| T3.7 | Implement `pages/settings.py` — DB connections CRUD, active selector, Test Connection | L | T1.2, T1.3 | Add/edit/delete + test works |
| T3.8 | Settings page — FastAPI endpoint config + Test API | M | T1.3, T2.2 | Health check shows router status |
| T3.9 | Settings page — schema selection config (embedding model, top-K, min score) + Save | M | T1.6, T3.7 | Pipeline uses saved values on Execute |

---

## Stage 4 — Polish & Tests

| ID | Task | Complexity | Depends | Acceptance |
|----|------|------------|---------|------------|
| T4.1 | Error UX — inline messages on validation/model/DB failures | M | T3.6 | Errors in log + SQL panel |
| T4.2 | Keyboard shortcut note in UI (Streamlit limitation: document Cmd+Enter via form submit pattern if feasible) | S | T3.3 | README + UI hint |
| T4.3 | Unit tests: `test_settings_store.py` | M | T1.2 | pytest green |
| T4.4 | Unit tests: `test_connection_tester.py` (mocked HTTP + DB) | M | T1.3 | pytest green |
| T4.5 | Unit tests: `test_schema_selector.py` | M | T1.6 | pytest green |
| T4.6 | Unit tests: `test_fastapi_client.py`, `test_activity_logger.py`, `test_safety_validator.py` | M | T2.* | pytest green |
| T4.7 | Unit tests: `test_schema_loader.py`, `test_executor.py` | M | T1.* | pytest green |
| T4.8 | Integration test: `test_text2sql_pipeline.py` (mocked FastAPI + schema selector) | L | T2.6 | pytest green |
| T4.9 | Manual test checklist — Settings, schema selection logs, FastAPI Execute | M | T3.9 | Documented in README |

---

## Stage 5 — Extensibility Stubs

| ID | Task | Complexity | Depends | Acceptance |
|----|------|------------|---------|------------|
| T5.1 | Implement `ui/tabs/sql2nosql_tab.py` — placeholder + "Coming soon" | S | T3.1 | Tab renders |
| T5.2 | Implement `ui/tabs/docs_tab.py` — static markdown (usage, safety rules, supported SQL) | S | T3.1 | Tab renders |
| T5.3 | Adapter registry in `ui/shell.py` for future tab registration | S | T2.2, T5.1 | New adapter = one registration line |

---

## Dependency Graph (summary)

```
T0.* → T1.* → T2.* → T3.* → T4.*
              ↘ T5.* (parallel after T3.1)
```

**Critical path:** T0 → T1.2 → T1.5 → T1.6 → T2.5 → T2.6 → T3.6 → T3.9 → T4.9

---

## Estimated Effort

| Stage | Tasks | Estimate |
|-------|-------|----------|
| 0 Scaffold | 6 | 0.5 day |
| 1 Core | 8 | 2.5 days |
| 2 FastAPI/Pipeline | 7 | 1.5 days |
| 3 UI + Settings | 9 | 2.5 days |
| 4 Polish/Tests | 9 | 1.5 days |
| 5 Stubs | 3 | 0.5 day |
| **Total** | **42** | **~9 days** |

---

## File Ownership Map

All paths relative to repo root under `tool/`:

| Module | Owner stage |
|--------|-------------|
| `app.py`, `pages/settings.py`, `config.py` | 0, 3 |
| `core/settings_store.py`, `core/connection_tester.py` | 1 |
| `core/schema_selector.py` | 1 |
| `core/inference/fastapi_client.py` | 2 |
| `adapters/*`, `pipeline/*` | 2 |
| `ui/*` | 3, 5 |
| `tests/*` | 4 |

**No new code outside `tool/`** except optional one-line mention in root README linking to `tool/README.md`.
