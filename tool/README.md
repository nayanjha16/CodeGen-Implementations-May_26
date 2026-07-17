# AI SQL Assistant (Desktop)

Standalone **desktop application** for interactive Text-to-SQL against PostgreSQL. Inference runs through the **hf-deploy FastAPI** service — this app does not load LoRA adapters locally.

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Python 3.11+** | Same environment as the main repo |
| **PostgreSQL** | Sample DVD database (see [Database setup](#database-setup)) |
| **hf-deploy API** | Local FastAPI server on port `8000` for SQL generation |
| **Docker** (recommended) | For the bundled PostgreSQL setup script |
| **`psql` or Docker** | Setup script uses local `psql` when available, otherwise `docker compose exec` |

Install Python dependencies from the repo root:

```bash
cd /path/to/CodeGen-Implementations-May_26
pip install -r tool/requirements.txt
pip install -r hf-deploy/requirements.txt   # for the inference server
```

Optional: copy the env template for first-run settings seed:

```bash
cp tool/.env.example tool/.env
```

## Database setup

The tool expects a PostgreSQL database with a realistic schema for Text-to-SQL demos. The bundled **`tool/test.sql`** dump is the Pagila DVD rental schema (tables such as `actor`, `film`, `customer`, `rental`).

### Option A — automated setup (recommended)

Uses the same PostgreSQL credentials as `/Volumes/Work/TEND` (`tend` / `tend` on port `5432`). The script starts Docker if PostgreSQL is not already running, creates database **`dvd`**, and loads the dump.

```bash
chmod +x tool/scripts/setup_dvd_database.sh
./tool/scripts/setup_dvd_database.sh
```

Use an existing TEND PostgreSQL container explicitly:

```bash
./tool/scripts/setup_dvd_database.sh --use-tend
```

Use the tool's standalone PostgreSQL container instead:

```bash
./tool/scripts/setup_dvd_database.sh --use-tool-docker
```

Drop and reload the database:

```bash
./tool/scripts/setup_dvd_database.sh --force
```

Then set the connection in `tool/.env`:

```env
DATABASE_URL=postgresql+psycopg://tend:tend@localhost:5432/dvd
```

Or add the same values in **Settings → Database** in the desktop app.

### Option B — reuse TEND Docker manually

If you already run PostgreSQL from the TEND project:

```bash
cd /Volumes/Work/TEND
docker compose up -d postgres
cd /path/to/CodeGen-Implementations-May_26
./tool/scripts/setup_dvd_database.sh --no-docker
```

## Start hf-deploy (inference server)

The desktop app sends prompts to the OpenAI-compatible **hf-deploy** API. Start it before running **Execute** in the Text-to-SQL tab.

**Terminal 1 — local adapter weights (fastest if checkpoints exist):**

```bash
cd /path/to/CodeGen-Implementations-May_26
pip install -r hf-deploy/requirements.txt
PYTHONPATH=hf-deploy uvicorn hf_deploy.api.app:app --host 0.0.0.0 --port 8000
```

**Alternative — load adapters from Hugging Face Hub:**

```bash
export HF_DEPLOY_ADAPTER_SOURCE=hub
export HF_ORG=care2achieve
PYTHONPATH=hf-deploy uvicorn hf_deploy.api.app:app --host 0.0.0.0 --port 8000
```

Verify the server:

```bash
curl http://localhost:8000/health
```

Default FastAPI settings in the tool match this endpoint (`http://localhost:8000/v1`, model `codegen-text2sql`). See [hf-deploy/README.md](../hf-deploy/README.md) for full configuration.

## Quick start

```bash
cd /path/to/CodeGen-Implementations-May_26

# 1. PostgreSQL + dvd sample data
./tool/scripts/setup_dvd_database.sh

# 2. Inference server (separate terminal)
PYTHONPATH=hf-deploy uvicorn hf_deploy.api.app:app --host 0.0.0.0 --port 8000

# 3. Desktop app
cp tool/.env.example tool/.env   # optional; seeds DATABASE_URL + FastAPI defaults
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

1. **Database** — run `./tool/scripts/setup_dvd_database.sh`; confirm `dvd` database exists
2. **Settings → Database** — connection `tend@localhost:5432/dvd`, Test Connection, set active
3. **Settings → FastAPI** — set base URL / model, Test API (requires hf-deploy running)
4. **Settings → Schema** — confirm embedding model and top-K saved
5. **Text-to-SQL tab** — enter a question, Execute (Ctrl/Cmd+Enter)
6. Verify activity log shows `schema_loaded`, `tables_selected`, `prompt_built`, `sql_generated`, `validation_passed`, `rows_retrieved`
7. Confirm validation blocks non-SELECT SQL (check activity log on failure)
8. **Clear** resets query, SQL, results, and activity log

## Architecture

```
tool/
├── app.py              # Desktop entry point
├── docker-compose.yml  # Standalone PostgreSQL (same creds as TEND)
├── scripts/
│   └── setup_dvd_database.sh
├── desktop/            # CustomTkinter UI
├── core/               # Settings, DB, schema, inference, validation
├── pipeline/           # Text-to-SQL orchestration
└── adapters/           # Tab extensibility (+ desktop/registry.py)
```

Reuses `src/text2sql/` for prompt building and syntax validation only.

## Troubleshooting

| Issue | Action |
|-------|--------|
| No active connection | Run `./tool/scripts/setup_dvd_database.sh`; set `DATABASE_URL` or add connection in Settings |
| Port 5432 already in use | Use existing TEND PostgreSQL with `--no-docker`, or stop the other container |
| FastAPI errors on Execute | Settings → Test API; start hf-deploy on port 8000 |
| Empty SQL extracted | Check model response format; see activity log `sql_generated` |
| Slow first Execute | Embedding model downloads once to `tool/.local/models/` on first schema selection; later runs load from cache |
| hf-deploy first start slow | Base model + adapters download on first request; see [hf-deploy/README.md](../hf-deploy/README.md) |
