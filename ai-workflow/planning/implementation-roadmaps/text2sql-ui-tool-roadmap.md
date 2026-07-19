# Implementation Roadmap — AI SQL Assistant (Streamlit UI)

> **Feature:** `text2sql-ui-tool`  
> **Plan:** `feature-plans/text2sql-ui-tool-plan.md`  
> **Tasks:** `task-breakdowns/text2sql-ui-tool-tasks.md`

---

## Milestones

| Milestone | Stage | Target outcome | Validation checkpoint |
|-----------|-------|----------------|---------------------|
| **M0 — Runnable shell** | 0 | `streamlit run tool/app.py` launches with tabs | App opens in browser |
| **M1 — Settings & DB layer** | 1 | Settings store, connection tester, schema loader + **schema selector** | pytest for core modules |
| **M2 — FastAPI pipeline** | 2 | FastAPI client only; pipeline with schema selection | Pipeline test with mocked API |
| **M3 — Full UI + Settings page** | 3 | Text-to-SQL tab + Settings (DB, FastAPI, schema selection config) | Manual E2E with hf-deploy running |
| **M4 — Release ready** | 4 | Tests pass, errors handled, README complete | Checklist in README |
| **M5 — Extensible shell** | 5 | Stub tabs + adapter registry | SQL2NoSQL tab shows placeholder |

---

## Implementation Order

```
Week 1
├── Day 1: Stage 0 + Stage 1 start (settings store, connection tester, database)
├── Day 2: Stage 1 complete (schema loader, **schema selector**, validator, executor)
├── Day 3: Stage 2 (FastAPI client, SQL extraction, pipeline)
├── Day 4: Stage 3 UI panels + Text-to-SQL tab
├── Day 5: Stage 3 Settings page (DB connections, FastAPI config, test buttons)
└── Day 6–7: Stage 4 tests + manual validation (schema selection + FastAPI Execute)
```

---

## Stage Details

### Stage 0 — Scaffold (M0)

**Goal:** Empty but runnable Streamlit app with project structure.

**Deliverables:**
- `tool/` folder tree
- `requirements.txt`, `.env.example`, `config.yaml`, `README.md`
- Stub `app.py` with three tabs

**Checkpoint:** `streamlit run tool/app.py` — no import errors.

---

### Stage 1 — Core Services + Settings (M1)

**Goal:** Persisted settings, connection testing, database layer without main UI.

**Deliverables:**
- `SettingsStore` — connections + FastAPI + schema selection config
- `connection_tester` — `test_database()` and `test_fastapi()`
- Schema introspection + **prompt-based table selection** (embeddings)
- Read-only validator, executor

**Checkpoint:**
```bash
pytest tool/tests/test_settings_store.py tool/tests/test_schema_selector.py -q
```

---

### Stage 2 — FastAPI Inference (M2)

**Goal:** Single inference path via deployed FastAPI; no local LoRA loading.

**Deliverables:**
- `FastApiInferenceClient` only (no local client)
- SQL extraction from API response
- `Text2SqlPipeline` with schema selection before prompt build

**Prerequisite:** hf-deploy API running with text2sql LoRA mounted.

**Checkpoint:**
```bash
cd hf-deploy && uvicorn hf_deploy.api.app:app --port 8000
pytest tool/tests/test_fastapi_client.py tool/tests/test_text2sql_pipeline.py -q
```

---

### Stage 3 — UI + Settings Page (M3)

**Settings page sections:**
1. **Database connections** — add/edit/delete, active selector, **Test Connection**
2. **FastAPI endpoint** — URL, API key, model, intent, **Test API**
3. **Schema selection** — embedding model, top-K, min score
4. **Execution limits** — optional

**Checkpoint:** Manual E2E:
1. Start hf-deploy API (LoRA loaded there)
2. Settings → add PG connection → Test Connection ✅
3. Settings → configure FastAPI → Test API ✅
4. Text-to-SQL → ask question → verify `tables_selected` in log → Execute → results

---

### Stage 4 — Polish & Tests (M4)

**Goal:** Production-quality error handling and test coverage.

**Deliverables:**
- All unit/integration tests green
- Error states for model/validation/DB failures
- README with setup and troubleshooting

**Checkpoint:**
```bash
pytest tool/tests/ -q
```

Manual checklist (see plan AD-8, success criteria).

---

### Stage 5 — Extensibility Stubs (M5)

**Goal:** Prove tab + adapter architecture for future SQL-to-NoSQL.

**Deliverables:**
- SQL-to-NoSQL placeholder tab
- Documentation tab with static content
- Adapter registry pattern

**Checkpoint:** Switch tabs without errors; docs tab shows safety rules.

---

## Testing Checkpoints

| When | What | Command / action |
|------|------|----------------|
| After Stage 1 | Settings + core | `pytest tool/tests/test_settings_store.py tool/tests/test_connection_tester.py` |
| After Stage 2 | Inference + pipeline | `pytest tool/tests/test_fastapi_client.py tool/tests/test_text2sql_pipeline.py` |
| After Stage 3 | Settings page manual | Test Connection + Test API buttons |
| After Stage 4 | Full suite | `pytest tool/tests/` |
| Before merge | Lint (optional) | `ruff check tool/` if configured |

---

## Rollout

1. **Internal demo** — team runs against sample PostgreSQL (e.g. Spider-style schema)
2. **Document env** — `tool/.env.example` + root model env vars
3. **No deployment artifact in MVP** — local Streamlit only; HF Space / Docker optional follow-up

---

## Post-MVP Backlog (not in initial roadmap)

| Item | Priority |
|------|----------|
| SQL-to-NoSQL tab (wire `src/sql2nosql/`) | P1 |
| Encrypted password storage | P2 |
| Query history in session / file | P3 |
| Docker Compose (PG + app) | P3 |
