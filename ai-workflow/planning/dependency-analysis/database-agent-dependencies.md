# Dependency Analysis — AI Database Agent

> **Feature:** `database-agent`  
> **Date:** 2026-07-26

---

## 1. Cross-Module Dependencies (within `agent/`)

```
agent/config/settings.py          → os.environ, dotenv (root + agent/.env)
        │
        ├── agent/database/profiles.py
        ├── agent/database/postgres.py   → sqlalchemy, psycopg
        ├── agent/database/mongodb.py    → pymongo
        │         └── agent/database/mongo_shell.py
        │
        ├── agent/clients/codegen_client.py
        │         └── src.text2sql / sql2nosql / documentation prompt builders (import)
        ├── agent/clients/orchestrator_llm.py → httpx → Ollama /api/chat
        │
        ├── agent/tools/schema_tool.py     → database/postgres, mongodb, profiles
        ├── agent/tools/fastapi_tool.py    → codegen_client
        ├── agent/tools/execution_tool.py  → database/postgres, mongodb
        │
        ├── agent/lib/sql_validation.py    → src.text2sql.sql_validator (import)
        ├── agent/lib/sql_repair.py        → sql_validation, text2sql_hints
        ├── agent/lib/text2sql_hints.py    → (standalone helpers)
        │
        ├── agent/orchestrator/intent_detector.py → orchestrator_llm
        ├── agent/orchestrator/planner.py
        ├── agent/orchestrator/retry.py    → fastapi_tool, execution_tool
        ├── agent/orchestrator/prompts.py
        │
        ├── agent/orchestration/graph.py   → langgraph
        ├── agent/orchestration/runner.py  → graph, tools, sql_repair, hints
        ├── agent/main.py                  → runner (CLI)
        │
        ├── agent/mcp/registry.py          → tools (shared handlers)
        ├── agent/mcp/server.py              → mcp SDK, registry
        │
        └── agent/web/app.py               → runner (async), FastAPI
```

**Constraint:** No edits to `src/` or `fastapi-deploy/` — agent imports from `src` at runtime only.

---

## 2. External Services

| Dependency | Role | Required for |
|------------|------|--------------|
| **CodeGen API** (Cloud Run) | LoRA v3 inference via `/v1/chat/completions` | text2sql, sql2nosql, nosql2doc |
| **Ollama** (`OLLAMA_BASE_URL`) | Orchestrator: intent, explain, summarize | All NL paths |
| **TEND Docker** | Postgres + Mongo on localhost | Integration tests, tend profile |
| **Standalone Postgres/Mongo** | Chinook / Northwind demos | Capstone demo (default) |

Default Cloud Run URL (from `agent/.env.example`):

`https://codegen-api-161349047936.asia-south2.run.app`

---

## 3. External Python Packages (`agent/requirements.txt`)

| Package | Purpose | Required |
|---------|---------|----------|
| `langgraph` | Agent workflow graph | Yes |
| `mcp` | MCP stdio server | Yes |
| `httpx` | CodeGen + Ollama HTTP | Yes |
| `fastapi` + `uvicorn` | Web UI (`agent/web/`) | Yes (web demo) |
| `sqlalchemy` + `psycopg[binary]` | Postgres read-only execution | Yes |
| `pymongo` | Mongo shell execution | Yes |
| `python-dotenv` | Config loading | Yes |
| `pytest` | Test suite | Dev |

Root `requirements.txt` is **not** required to run the agent if `agent/requirements.txt` is installed and `PYTHONPATH` includes repo root (for `src` imports).

---

## 4. Reuse from Existing Repo

| Need | Source | Approach |
|------|--------|----------|
| Prompt shape (train/eval parity) | `src/text2sql`, `src/sql2nosql`, `src/documentation` | Import in `codegen_client.py` |
| SQL validation rules | `src/text2sql/sql_validator.py` | Import in `agent/lib/sql_validation.py` |
| Inference | `fastapi-deploy/codegen_api` | HTTP only — no local PEFT |
| DB naming (TEND) | TEND Docker conventions | `database/profiles.py` |
| Eval gold set | `data/spider_gold_validation.jsonl` | Unchanged — agent demos use standalone DBs |

---

## 5. Ordering Constraints

1. `config/settings.py` + `database/*` before tools.
2. `codegen_client.py` before `fastapi_tool.py`.
3. Tools before orchestrator + LangGraph.
4. LangGraph runner before MCP registry (MCP delegates to tools).
5. Runner stable before Web UI (`agent/web/`).
6. Cloud Run LoRA **v3** published before live text2sql demo.

---

## 6. Risks

| Risk | Mitigation |
|------|------------|
| CodeGen invents invalid WHERE filters | `strip_invented_where_filters`, DDL hints in `postgres.py` |
| Incomplete SELECT (missing join columns) | `lib/sql_repair.py` post-process |
| Ollama hallucinated summaries | `format_listing_summary()` deterministic path |
| 30–90s latency (CodeGen + Ollama) | Web UI async + 3-min timeout + progress indicator |
| Chinook PascalCase identifiers | Quoted DDL in schema tool; lowercase Mongo collections |
| Docker not running | Integration tests skip via `pytest` markers |

---

## 7. File Index

| Document | Path |
|----------|------|
| Feature plan | `ai-workflow/planning/feature-plans/database-agent-plan.md` |
| Task breakdown | `ai-workflow/planning/task-breakdowns/database-agent-tasks.md` |
| Roadmap | `ai-workflow/planning/implementation-roadmaps/database-agent-roadmap.md` |
| Approval | `ai-workflow/planning/approvals/database-agent-approval.md` |
