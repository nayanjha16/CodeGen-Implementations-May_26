# Dependency Analysis — AI SQL Assistant (Streamlit UI)

> **Feature:** `text2sql-ui-tool`  
> **Updated:** 2026-07-16 — FastAPI-only inference; prompt-based schema selection

---

## 1. Internal Module Dependencies

```
tool/app.py
  └── ui/shell.py
        ├── ui/tabs/text2sql_tab.py
        │     └── pipeline/text2sql_pipeline.py
        │           ├── core/schema_loader.py
        │           ├── core/schema_selector.py   ← user prompt
        │           ├── core/inference/fastapi_client.py
        │           └── core/database.py, executor
        └── pages/settings.py
              ├── core/settings_store.py
              └── core/connection_tester.py
```

### Ordering constraints

| Module | Must exist before |
|--------|-------------------|
| `core/settings_store.py` | database, Settings page, fastapi_client |
| `core/schema_loader.py` | `schema_selector`, pipeline |
| `core/schema_selector.py` | `text2sql_adapter`, pipeline |
| `core/inference/fastapi_client.py` | pipeline, Settings Test API |
| `pages/settings.py` | settings_store, connection_tester |

---

## 2. External Repo Dependencies

### `src/` (prompt + validation only — no model loading)

| Module | Used by | Purpose |
|--------|---------|---------|
| `src.text2sql.prompt_builder` | `text2sql_adapter.py` | Prompt template |
| `src.text2sql.sql_generator` | SQL extraction helper | Parse API response (no model) |
| `src.text2sql.sql_validator` | `text2sql_adapter.py` | Syntax validation |
| `src.utils.config.load_config` | `config.py` | Optional yaml merge |

**Explicitly NOT used by tool:**
- `src.models.model_loader` — LoRA not loaded in tool
- `src/evaluation/database_execution.py` — TEND eval only

### hf-deploy FastAPI (required for inference)

| Endpoint | Used by | Purpose |
|----------|---------|---------|
| `GET /health` | `connection_tester` | Test API |
| `POST /v1/chat/completions` | `fastapi_client.py` | Text-to-SQL generation |
| LoRA adapter (server-side) | hf-deploy router | Model inference |

---

## 3. External Service & Runtime Dependencies

| Dependency | Type | Required | Notes |
|------------|------|----------|-------|
| PostgreSQL | Database | Yes | User-provided |
| **hf-deploy FastAPI** | HTTP service | **Yes** | LoRA adapter deployed here |
| sentence-transformers | Python package | Yes | Local schema selection only |
| httpx | Python package | Yes | FastAPI client |
| torch/peft/transformers | — | **No (in tool)** | Only on FastAPI server |

---

## 4. Environment Variables

| Variable | Source | Used by |
|----------|--------|---------|
| `DATABASE_URL` | `tool/.env` | Seed first connection |
| `FASTAPI_BASE_URL` | `tool/.env` | Default API URL in settings |
| `FASTAPI_API_KEY` | `tool/.env` | Optional bearer token |
| `SCHEMA_TOP_K` | settings / env | `schema_selector.py` |
| `EMBEDDING_MODEL` | settings / env | Default `BAAI/bge-small-en-v1.5` |

LoRA/model env vars (`MODEL_ADAPTER`, etc.) are consumed by **hf-deploy**, not the tool.

---

## 5. Python Package Install

```bash
# Streamlit tool (lightweight — no torch/peft)
pip install -r tool/requirements.txt

# FastAPI server (separate process — has LoRA)
cd hf-deploy && pip install -r requirements.txt
uvicorn hf_deploy.api.app:app --port 8000
```

---

## 6. Risk Dependencies

| If unavailable | Impact | Fallback |
|----------------|--------|----------|
| FastAPI down | Cannot generate SQL | Test API on Settings; block Execute |
| PG not running | Cannot execute | Can still test API path partially |
| Embedding model missing | Schema selection fails | Log error; optional fallback: all tables if count ≤ top_k |
| Wrong tables selected | Bad SQL | Log scores; tune top-K; FK expansion |

---

## 7. Test Dependencies

| Test | Mocks |
|------|-------|
| `test_schema_selector` | Fixed embedding vectors or mocked SentenceTransformer |
| `test_fastapi_client` | httpx mock / respx |
| `test_text2sql_pipeline` | Mock FastAPI + mock DB + mock selector |
| Manual E2E | Real PG + running hf-deploy |
