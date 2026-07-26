# Agent standalone demo database

Use this when you want a **custom Postgres database** for agent demos — separate from TEND gold eval.

**You choose the database** (Northwind, Chinook, Pagila, your own schema, etc.). Nothing here assumes DVD/Pagila.

Eval scripts (`scripts/run_baseline_eval.py`) still use TEND only — unchanged.

---

## Two profiles

| Profile | Env | Postgres | Mongo |
|---------|-----|----------|-------|
| **tend** (default) | `AGENT_DB_PROFILE=tend` | `tend_spider` / schema = `db_id` | `{dataset}_{db_id}` |
| **standalone** | `AGENT_DB_PROFILE=standalone` | **you configure** | **you configure** |

When you pick a database, set these in **`agent/.env`** (see `agent/.env.example`):

```bash
AGENT_DB_PROFILE=standalone
AGENT_DEMO_DB_ID=chinook          # or northwind
AGENT_DEMO_POSTGRES_DATABASE=chinook
AGENT_DEMO_POSTGRES_SCHEMA=public
AGENT_DEMO_MONGO_DATABASE=chinook
AGENT_DEMO_SQL_DUMP=agent/data/standalone/chinook/test.sql
```

**Preloaded demos:** Northwind and Chinook — see `agent/data/standalone/README.md`.

---

## How to create a `test.sql` for **your** database

A file like `tool/test.sql` is a **PostgreSQL plain-text dump** from `pg_dump`.

### Step 1 — Pick a sample database

| Option | Domain | Source |
|--------|--------|--------|
| **Northwind** | Orders / products | [pthom/northwind_psql](https://github.com/pthom/northwind_psql) |
| **Pagila** | Film rental (DVD-like) | [devrimgunduz/pagila](https://github.com/devrimgunduz/pagila) |
| **Chinook** | Music store | SQLite → convert with [pgloader](https://pgloader.io/) |
| **TEND BIRD schema** | Eval-aligned | `pg_dump` one schema from `tend_bird` after import |
| **Your own** | Anything | Write CREATE TABLE + INSERT, load, export |

### Step 2 — Load into Postgres

```sql
CREATE DATABASE northwind;
```

```powershell
# via psql or docker exec
psql -U tend -d northwind -f path\to\northwind.sql
```

Or use the setup script once you have the dump file:

```powershell
$env:AGENT_DEMO_POSTGRES_DATABASE = "northwind"
$env:AGENT_DEMO_SQL_DUMP = "agent\data\standalone\northwind.sql"
.\agent\scripts\setup_demo_postgres.ps1 -UseTend -Force
```

### Step 3 — Export your canonical dump (optional, for portability)

```powershell
python agent/scripts/export_postgres_demo.py `
  --database northwind `
  --schema public `
  --output agent/data/standalone/northwind.sql
```

Via Docker:

```powershell
docker exec tend-postgres-1 pg_dump -U tend -d northwind --schema=public --no-owner --no-privileges `
  > agent/data/standalone/northwind.sql
```

Schema-only (smaller, no row data):

```powershell
python agent/scripts/export_postgres_demo.py --database northwind --schema-only `
  --output agent/data/standalone/northwind_schema.sql
```

### Step 4 — Mirror to Mongo (for sql2nosql execution)

```powershell
$env:AGENT_DEMO_MONGO_DATABASE = "northwind"
python agent/scripts/mirror_postgres_to_mongo.py --force
```

### Step 5 — Verify

```powershell
$env:PYTHONPATH = (Get-Location).Path
$env:AGENT_DB_PROFILE = "standalone"
$env:AGENT_DEMO_DB_ID = "northwind"
$env:AGENT_DEMO_POSTGRES_DATABASE = "northwind"
$env:AGENT_DEMO_MONGO_DATABASE = "northwind"
python -c "from agent.database import PostgresExecutor; pg=PostgresExecutor(); s=pg.introspect_schema(profile='standalone'); print(len(s.tables), 'tables'); pg.close()"
```

---

## What makes a good demo database?

| Property | Why |
|----------|-----|
| 5–20 tables | Realistic joins; schema tool stays fast |
| Foreign keys | Better schema selection |
| Some data rows | Execution returns results |
| Plain `pg_dump` format | Works with setup scripts |

---

## Folder layout

```text
agent/data/standalone/
├── README.md
├── chinook/           # test.sql, questions.txt, CHINOOK.md
└── northwind/         # test.sql, questions.txt, NORTHWIND.md
```

Large `.sql` dumps live under each demo folder. Generate locally with `pg_dump` if missing.

---

## Prompt builders (Stage 2+)

Agent will import prompt builders from `src/` so prompts match training. Eval scripts use the same `src/` modules.
