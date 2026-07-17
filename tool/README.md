# AI SQL Assistant (Desktop)

Standalone **desktop application** for interactive Text-to-SQL against PostgreSQL. Inference runs through the **hf-deploy FastAPI** service — this app does not load LoRA adapters locally.

## Quick start

```bash
cd /path/to/CodeGen-Implementations-May_26

pip install -r tool/requirements.txt

# Optional: copy env template for first-run settings seed
cp tool/.env.example tool/.env

# Terminal 1 — inference (optional for full Execute)
cd hf-deploy && uvicorn hf_deploy.api.app:app --port 8000

# Launch desktop app
python tool/app.py
```

## Features

- Native desktop window (CustomTkinter) — no browser required
- Text-to-SQL tab: natural language → generate → validate → execute
- Settings dialog: PostgreSQL connections, FastAPI endpoint, schema selection
- Structured activity log panel
- Stub tabs for SQL-to-NoSQL and Documentation

## Settings

Open **Settings** from the main window to:

1. Add/edit PostgreSQL connections and set the active connection
2. Configure the FastAPI endpoint and run **Test API**
3. Tune schema selection (embedding model, top-K, min score)

Settings persist to `tool/.local/settings.json` (gitignored).

## Run tests

```bash
pytest tool/tests/ -q
```

## Manual test checklist

1. **Settings → Database** — add a PostgreSQL connection, Test Connection, set active
2. **Settings → FastAPI** — set base URL / model, Test API (requires hf-deploy running)
3. **Settings → Schema** — confirm embedding model and top-K saved
4. **Text-to-SQL tab** — enter a question, Execute (Ctrl/Cmd+Enter)
5. Verify activity log shows `schema_loaded`, `tables_selected`, `prompt_built`, `sql_generated`, `validation_passed`, `rows_retrieved`
6. Confirm validation blocks non-SELECT SQL (check activity log on failure)
7. **Clear** resets query, SQL, results, and activity log

## Architecture

```
tool/
├── app.py              # Desktop entry point
├── desktop/            # CustomTkinter UI
├── core/               # Settings, DB, schema, inference, validation
├── pipeline/           # Text-to-SQL orchestration
└── adapters/           # Tab extensibility (+ desktop/registry.py)
```

Reuses `src/text2sql/` for prompt building and syntax validation only.

## Troubleshooting

| Issue | Action |
|-------|--------|
| No active connection | Settings → add connection and set active |
| FastAPI errors on Execute | Settings → Test API; start hf-deploy on port 8000 |
| Empty SQL extracted | Check model response format; see activity log `sql_generated` |
| Slow first Execute | Embedding model downloads on first schema selection |
