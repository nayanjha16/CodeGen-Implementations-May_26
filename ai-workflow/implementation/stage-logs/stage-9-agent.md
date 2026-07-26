# Stage 9 — Capstone Demo Polish

**Date:** 2026-07-26  
**Status:** Complete  
**Plan:** [database-agent-plan.md](../../planning/feature-plans/database-agent-plan.md) Stage 9

## Implemented

- [x] `agent/scripts/run_capstone_demo.py` — scripted demo walkthrough
- [x] `agent/scripts/verify_demo_databases.py` — health check both demo DBs
- [x] `agent/data/standalone/chinook/questions.txt` — D1–D6 demo questions
- [x] `agent/data/standalone/northwind/questions.txt`
- [x] `agent/tests/test_capstone_demo_stage9.py`
- [x] `agent/README.md` — run instructions for CLI + MCP

## Demo DB verification

| Database | Postgres tables | Mongo collections | Agent layer |
|----------|-----------------|-------------------|-------------|
| chinook | 11 | 11 | ✅ introspect + execute |
| northwind | 14 | 14 | ✅ introspect + execute |

Default: **Chinook** (`AGENT_DEMO_DB_ID=chinook`).

## Recommended live demo questions

- **D1** — List album titles with artist names (2-table join)
- **D3** — How many customers?
- **D6** — Filter + order query

Avoid **D2** (3-table) — still flaky without manual SQL fix.

## Blockers

None when TEND Docker + Cloud Run + Ollama are running.

## Next (Stage 10)

Web UI + query quality improvements.
