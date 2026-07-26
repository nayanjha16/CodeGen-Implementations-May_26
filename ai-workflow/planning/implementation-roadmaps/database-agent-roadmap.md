# Implementation Roadmap — AI Database Agent

> **Feature:** `database-agent`  
> **Date:** 2026-07-26  
> **Approval:** `approvals/database-agent-approval.md` (APPROVED)

---

## Implementation Order

| Order | Stage | Key outputs | Status |
|-------|-------|-------------|--------|
| 1 | S1 — Config + DB layer | `config/settings.py`, `database/postgres.py`, `database/mongodb.py` | ✅ |
| 2 | S1b — Standalone demos | `profiles.py`, Chinook + Northwind data, setup scripts | ✅ |
| 3 | S2 — CodeGen client | `clients/codegen_client.py` (imports `src` prompts) | ✅ |
| 4 | S3 — Three tools | `tools/schema_tool.py`, `fastapi_tool.py`, `execution_tool.py` | ✅ |
| 5 | S4 — Validation | `lib/sql_validation.py` | ✅ |
| 6 | S5 — Orchestrator | `orchestrator/*`, `clients/orchestrator_llm.py` | ✅ |
| 7 | S6 — LangGraph + CLI | `orchestration/graph.py`, `runner.py`, `main.py` | ✅ |
| 8 | S7 — MCP server | `mcp/server.py`, `mcp/registry.py` | ✅ |
| 9 | S8 — Integration tests | `test_integration_stage8.py`, retry fix | ✅ |
| 10 | S9 — Capstone demo | Demo scripts, verify DBs, question sets | ✅ |
| 11 | S10 — Web UI + quality | `web/`, `sql_repair.py`, `text2sql_hints.py` | ✅ |

---

## Testing Checkpoints

### CP-1 — Database layer (after S1)
- [x] SQL validation unit tests pass without Docker
- [x] Mongo shell parser accepts TEND-style queries

### CP-2 — CodeGen client (after S2)
- [x] Mocked HTTP tests for all three intents
- [x] Prompt parity with `src` prompt builders

### CP-3 — Tools (after S3)
- [x] Schema tool returns DDL for Chinook `Customer`
- [x] Execution tool blocks DDL/DML

### CP-4 — LangGraph (after S6)
- [x] Graph tests for all five intents (mocked externals)
- [x] CLI `python -m agent.main` runs end-to-end

### CP-5 — MCP (after S7)
- [x] Registry dispatches `extract_schema`, `codegen_generate`, `execute_query`
- [x] `python -m agent.mcp.server` starts stdio transport

### CP-6 — Integration (after S8)
- [x] Live Chinook Postgres + Mongo when TEND Docker up
- [x] Retry path after execution error

### CP-7 — Capstone demo (after S9)
- [x] `verify_demo_databases.py` — both demos healthy
- [x] D1/D3/D6 demo questions succeed via CLI

### CP-8 — Web UI (after S10)
- [x] `python -m agent.web` → health + query API
- [x] **88** agent tests pass (`pytest agent/tests/ -q`)

---

## Rollout Strategy

- **Phase A:** Unit tests only (no Docker, mocked CodeGen/Ollama).
- **Phase B:** Local Docker + Cloud Run CodeGen v3 + Ollama — CLI demo.
- **Phase C:** MCP in Cursor + Web UI for capstone presentation.

---

## Demo Recommendations

| Demo ID | Question type | Notes |
|---------|---------------|-------|
| D1 | 2-table join (album + artist) | `sql_repair` ensures both columns in SELECT |
| D3 | Simple aggregate (count customers) | Reliable baseline |
| D6 | Filter + order | Good for showing execution + summary |
| D2 | 3-table join | Flaky — avoid in live demo |

---

## File Index

| Document | Path |
|----------|------|
| Feature plan | `ai-workflow/planning/feature-plans/database-agent-plan.md` |
| Task breakdown | `ai-workflow/planning/task-breakdowns/database-agent-tasks.md` |
| Dependencies | `ai-workflow/planning/dependency-analysis/database-agent-dependencies.md` |
| Approval | `ai-workflow/planning/approvals/database-agent-approval.md` |
| Validation | `ai-workflow/validation/validation-reports/database-agent-validation.md` |
| Stage logs | `ai-workflow/implementation/stage-logs/stage-*-agent.md` |
