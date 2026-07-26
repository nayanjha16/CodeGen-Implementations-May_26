# Feature Plan — AI Database Agent

> **Feature slug:** `database-agent`  
> **Date:** 2026-07-25 · **Complete:** 2026-07-26  
> **Spec:** [agent/doc/agent.md](../../../agent/doc/agent.md) (§1–§12)  
> **Approval:** [database-agent-approval.md](../approvals/database-agent-approval.md)  
> **Live status:** [current-state.md](../../context/current-state.md)

---

## 1. Scope

### In scope

Build the full **AI Database Agent** under `agent/` only (no edits to `src/` or `fastapi-deploy/`):

| Spec | Deliverable |
|------|-------------|
| FR-1 Intent | `orchestrator/intent_detector.py` |
| FR-2 Schema | `tools/schema_tool.py` |
| FR-3 Generation | `clients/codegen_client.py` → Cloud Run `/v1/chat/completions` |
| FR-4 Execution | `tools/execution_tool.py` + `database/postgres.py`, `mongodb.py` |
| FR-5 Retry (≤3) | `orchestrator/retry.py` + LangGraph loop |
| FR-6 NL answer | Ollama summarize + deterministic listing summaries |
| §7 MCP | `mcp/server.py`, `mcp/registry.py` |
| §8 Workflow | `orchestration/graph.py`, `runner.py`, `main.py` CLI |
| Capstone extension | `web/` — FastAPI chat UI |
| Quality | `lib/sql_repair.py`, `lib/text2sql_hints.py`, filter stripping |

**Five capabilities:** text2sql, sql2nosql, nosql2doc, explain SQL (Ollama), validate SQL (rules).

Agent **never generates SQL** — CodeGen LoRA v3 on Cloud Run does.

### Out of scope

- GPT-5 / OpenAI orchestrator
- Local LoRA inference in agent
- Edits to `src/` or `fastapi-deploy/`
- §13 future: conversation memory, human approval, vector schema (Phase 2 optional)
- Retrain LoRA for capstone

### Deliverables (code)

| Component | Path |
|-----------|------|
| Config + DB | `agent/config/`, `agent/database/` |
| HTTP clients | `agent/clients/codegen_client.py`, `orchestrator_llm.py` |
| Tools | `agent/tools/` (schema, fastapi, execution) |
| Orchestrator | `agent/orchestrator/`, `agent/orchestration/` |
| MCP | `agent/mcp/` |
| Web UI | `agent/web/` |
| Tests | `agent/tests/` (88 tests) |

**Related planning (no duplication here):**

| Doc | Path |
|-----|------|
| Tasks | [database-agent-tasks.md](../task-breakdowns/database-agent-tasks.md) |
| Roadmap | [database-agent-roadmap.md](../implementation-roadmaps/database-agent-roadmap.md) |
| Dependencies | [database-agent-dependencies.md](../dependency-analysis/database-agent-dependencies.md) |
| Validation | [database-agent-validation.md](../../validation/validation-reports/database-agent-validation.md) |
| Stage logs | [implementation/stage-logs/](../../implementation/stage-logs/) |

---

## 2. Architecture Decisions

### AD-1: HTTP adapter to Cloud Run (Q-1)

**Decision:** Client-only mapping to `POST /v1/chat/completions` + explicit `"intent"`. No `/generate/*` shim in `codegen_api`.

### AD-2: Two LLMs — separate roles

| Role | Engine |
|------|--------|
| Intent, summarize, explain | **Ollama** (`gemma3:4b` default; `qwen2.5:7b-instruct` optional) |
| SQL / Mongo / doc generation | **CodeGen LoRA v3** via Cloud Run |

### AD-3: LangGraph + MCP (Q-3)

Build Python tools + LangGraph first; MCP stdio server wraps the same handlers (no second implementation).

### AD-4: Code location (Q-2)

All new code under `agent/`. Import `src` prompt builders + sql_validator at runtime (`PYTHONPATH` = repo root).

### AD-5: DB execution separate (Q-8)

Direct psycopg + pymongo in `agent/database/` — do not import `src/evaluation/database_execution.py` (TEND `src` name clash).

### AD-6: Demo databases (Q-17)

| Profile | Env | Use |
|---------|-----|-----|
| `standalone` | `AGENT_DEMO_*` | Chinook (default), Northwind |
| `tend` | `db_id` | Gold / eval-aligned schemas |

### AD-7: Three intents, not forced chain (Q-18)

Orchestrator picks one path: text2sql **or** sql2nosql **or** nosql2doc — not always full pipeline.

### AD-8: Retry (Q-10, Q-11)

On validation or execution failure, append `Previous SQL` + `Database error` to prompt; max **3** attempts; `"intent": "text2sql"`.

### AD-9: Edge-case limits

- Max rows returned: **100**
- Empty schema → ask user to clarify
- 0 rows → explicit message, not fake results

---

## 3. API Adapter (spec vs deployed)

| Spec method | HTTP |
|-------------|------|
| `generate_sql` | `POST /v1/chat/completions` + `"intent": "text2sql"` |
| `generate_nosql` | + `"intent": "sql2nosql"` |
| `generate_documentation` | + `"intent": "nosql2doc"` |
| `health` | `GET /health` |

Prompt shape (matches training):

```text
Schema:
CREATE TABLE ...

Question:
...
```

---

## 4. Three Tools (MCP §7)

| Tool | Delegates to |
|------|--------------|
| `extract_schema` | `schema_tool` — Postgres/Mongo introspection, DDL |
| `codegen_generate` | `fastapi_tool` → `codegen_client` |
| `execute_query` | `execution_tool` — read-only Postgres + Mongo shell |

---

## 5. Intent → Tool Chains

| Intent | Chain | Execute? |
|--------|-------|----------|
| `text2sql` | schema → CodeGen → Postgres | Yes |
| `sql2nosql` | CodeGen → Mongo | Yes |
| `nosql2doc` | CodeGen | No |
| `explain_sql` | Ollama only | No |
| `validate_sql` | rules only | No |

---

## 6. Build Stages (complete)

| Stage | Work | Status |
|-------|------|--------|
| 1 | Config + DB layer | ✅ |
| 1b | Standalone demos (Chinook, Northwind) | ✅ |
| 2 | CodeGen HTTP client | ✅ |
| 3 | Three tools | ✅ |
| 4 | SQL validation | ✅ |
| 5 | Ollama orchestrator | ✅ |
| 6 | LangGraph + CLI | ✅ |
| 7 | MCP server | ✅ |
| 8 | Integration tests | ✅ |
| 9 | Capstone demo scripts | ✅ |
| 10 | Web UI + query quality fixes | ✅ |

---

## 7. Run

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m agent.main "How many customers are in the database?"
python -m agent.mcp.server
python -m agent.web   # http://127.0.0.1:8080
```

**Demo questions:** D1, D3, D6 in `agent/data/standalone/chinook/questions.txt`. Avoid D2 (3-table join).

---

## 8. Orchestrator LLM

Default: **`gemma3:4b`** via Ollama. Upgrade to **`qwen2.5:7b-instruct`** if intent/summary quality needs it (fits 24 GB RAM with Docker + Cloud Run inference).

Config: `AGENT_ORCHESTRATOR_MODEL` in `agent/.env`.

---

## 9. Reuse from `src/`

| Import | From |
|--------|------|
| Prompt builders | `src.text2sql`, `src.sql2nosql`, `src.documentation` |
| SQL validation | `src.text2sql.sql_validator` |

Separate in `agent/database/` for execution and introspection I/O shapes.

---

## 10. Known Limitations

- Latency 30–90s per query (CodeGen + Ollama + Postgres)
- CodeGen may omit join columns — mitigated by `sql_repair.py`
- D2 (3-table) still flaky for live demo
