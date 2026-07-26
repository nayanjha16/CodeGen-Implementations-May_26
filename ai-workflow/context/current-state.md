# Current State — AI Database Agent

> Updated: 2026-07-26

## Active initiative: AI Database Agent (`agent/`)

| Field | Value |
|-------|-------|
| **Phase** | Implementation — Stages 1–8 complete |
| **Spec** | `agent/doc/agent.md` |
| **Default demo** | Chinook (`AGENT_DEMO_DB_ID=chinook` in `agent/.env`) |
| **Next** | Stage 9 — CLI demo polish |

### Implementation status

| Component | Status |
|-----------|--------|
| Config + DB layer | ✅ |
| CodeGen HTTP client | ✅ |
| Three tools (schema, codegen, execution) | ✅ |
| SQL validation + retry | ✅ |
| LangGraph orchestrator + CLI | ✅ |
| MCP server (stdio) | ✅ |
| Integration / E2E tests | ✅ Stage 8 |

### Demo DB health

Both Chinook and Northwind verified via `python agent/scripts/verify_demo_databases.py`.

### Run

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m agent.main "How many customers are in the database?"
python -m agent.mcp.server   # MCP stdio
```

---

## Infrastructure

- CodeGen API: `https://codegen-api-161349047936.asia-south2.run.app` (LoRA v3)
- Ollama orchestrator: `gemma3:4b` local
- TEND Docker: Postgres + Mongo on localhost
