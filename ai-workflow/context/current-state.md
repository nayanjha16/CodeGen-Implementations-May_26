# Current State — AI Database Agent

> Updated: 2026-07-26

## Active initiative: AI Database Agent (`agent/`)

| Field | Value |
|-------|-------|
| **Phase** | **Complete** — Stages 1–10 |
| **Spec** | `agent/doc/agent.md` |
| **Default demo** | Chinook (`AGENT_DEMO_DB_ID=chinook` in `agent/.env`) |
| **Tests** | **88 passed** (`pytest agent/tests/ -q`) |
| **Validation** | [database-agent-validation.md](../validation/validation-reports/database-agent-validation.md) |

### Implementation status

| Component | Status |
|-----------|--------|
| Config + DB layer | ✅ |
| Standalone demo profile (Chinook, Northwind) | ✅ |
| CodeGen HTTP client | ✅ |
| Three tools (schema, codegen, execution) | ✅ |
| SQL validation + retry | ✅ |
| LangGraph orchestrator + CLI | ✅ |
| MCP server (stdio) | ✅ |
| Integration / E2E tests | ✅ |
| Project demo scripts | ✅ |
| Web UI + SQL repair + hints | ✅ |

### Demo DB health

Both Chinook and Northwind verified via `python agent/scripts/verify_demo_databases.py`.

### Run

```powershell
$env:PYTHONPATH = (Get-Location).Path

# CLI
python -m agent.main "How many customers are in the database?"

# MCP (stdio)
python -m agent.mcp.server

# Web UI
python -m agent.web
# → http://127.0.0.1:8080
```

### Recommended live demo questions

- **D1** — List album titles with artist names
- **D3** — Which artist has the most albums?
- **D6** — Filter + order query

Avoid **D2** (3-table join) — still flaky.

---

## Planning

[database-agent-plan.md](../planning/feature-plans/database-agent-plan.md) · [database-agent-validation.md](../validation/validation-reports/database-agent-validation.md)
