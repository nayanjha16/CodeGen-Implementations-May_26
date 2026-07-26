# Stage 1 — Config + database layer

**Date:** 2026-07-25  
**Plan:** [implementation-plan.md](../../planning/feature-plans/agent/implementation-plan.md) Stage 1

## Implemented

- [x] `agent/config/settings.py` — Postgres, Mongo, CodeGen API, Ollama, agent limits
- [x] `agent/database/postgres.py` — read-only SQL, schema introspection, DDL export
- [x] `agent/database/mongodb.py` — shell query execution, collection listing
- [x] `agent/database/mongo_shell.py` — minimal TEND-compatible shell parser
- [x] `agent/requirements.txt`, `agent/.env.example`
- [x] `agent/tests/test_database_stage1.py` — SQL validation + mongo parse (no Docker)

## Changed files

All new under `agent/` — no edits to `src/` or `fastapi-deploy/`.

## Assumptions

- TEND Docker uses `tend_{dataset}` Postgres catalogs and `{dataset}_{db_id}` Mongo DB names
- Root `.env` is loaded when `agent/.env` is absent
- LoRA **v3** will be promoted to Cloud Run (`CODEGEN_API_URL`) after publish

## Blockers

None for Stage 1.

## Stage 1b — Standalone profile (generic, 2026-07-26)

- [x] `agent/database/profiles.py` — `tend` vs `standalone` (any custom DB you configure)
- [x] `agent/config/settings.py` — `AGENT_DEMO_*` env vars (no hardcoded DVD)
- [x] `agent/data/README.md` — how to create `.sql` for **your chosen** database
- [x] Setup/mirror/export scripts — require `AGENT_DEMO_*` to be set explicitly

Eval scripts unchanged.

## Next (Stage 2)

- `agent/clients/codegen_client.py` — HTTP `/v1/chat/completions` + `intent`
