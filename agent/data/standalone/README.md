# Standalone agent demo databases

Load **one or more** public Postgres samples in TEND Docker. The agent uses **`agent/.env`** only — no per-demo env files.

| Demo | Postgres / Mongo DB | Questions |
|------|---------------------|-----------|
| **Chinook** (default) | `chinook` | `chinook/questions.txt` |
| **Northwind** | `northwind` | `northwind/questions.txt` |

Both can coexist in Docker. Switch active demo at runtime or via env.

## Switch demo

**Runtime** (no `.env` edit):

```powershell
python -m agent.main --db-id northwind "How many customers do we have?"
```

**Persistent** — set in `agent/.env`:

```env
AGENT_DEMO_DB_ID=chinook   # or northwind
AGENT_DEMO_SQL_DUMP=agent/data/standalone/chinook/test.sql
```

Postgres/Mongo database names default to `AGENT_DEMO_DB_ID` unless overridden.

**TEND eval** — set `AGENT_DB_PROFILE=tend` (gold eval unchanged).

See [../README.md](../README.md) for adding another public sample.
