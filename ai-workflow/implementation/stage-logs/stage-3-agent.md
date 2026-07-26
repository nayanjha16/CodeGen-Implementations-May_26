# Stage 3 — Three MCP Tools

**Date:** 2026-07-25  
**Status:** Complete  
**Plan:** [database-agent-plan.md](../../planning/feature-plans/database-agent-plan.md) Stage 3

## Implemented

- [x] `agent/tools/schema_tool.py` — Postgres/Mongo introspection, DDL export, table selection
- [x] `agent/tools/fastapi_tool.py` — delegates to `codegen_client` (sql, nosql, documentation)
- [x] `agent/tools/execution_tool.py` — read-only Postgres + Mongo shell execution
- [x] `agent/tests/test_tools_stage3.py`

## Tool contracts (spec §7)

| Tool | Input | Output |
|------|-------|--------|
| Schema | `question`, `db_id` | tables, columns, relationships, `schema_ddl` |
| CodeGen | operation + payload | generated SQL / Mongo / doc text |
| Execution | `query`, `db_id`, `engine` | rows, success, error |

## Assumptions

- Agent never generates SQL in-process — all generation via HTTP
- Chinook uses quoted PascalCase table names in DDL

## Blockers

None.

## Next (Stage 4)

SQL validation wrapper before execution.
