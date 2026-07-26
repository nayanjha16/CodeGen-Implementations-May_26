# Agent Planning — Current Status

> **Last updated:** 2026-07-26  
> **Spec:** [../../../../agent/doc/agent.md](../../../../agent/doc/agent.md) (full §1–§12)  
> **Initial demo DB:** **Chinook** (`AGENT_DB_PROFILE=standalone`)  
> **CodeGen API:** LoRA **v3** on Cloud Run (published)

---

## Build progress

| Stage | Status | Deliverable |
| --- | --- | --- |
| **1** | ✅ Done | `config/settings.py`, `database/postgres.py`, `database/mongodb.py`, `mongo_shell.py` |
| **1b** | ✅ Done | Standalone demo profile, `database/profiles.py`, setup/mirror scripts, demo data |
| **2** | ✅ Done | `clients/codegen_client.py` — HTTP + **import prompt builders from `src/`** |
| **3** | ✅ Done | `tools/schema_tool.py`, `fastapi_tool.py`, `execution_tool.py` |
| **4** | ✅ Done | `lib/sql_validation.py` (import from `src`) |
| **5** | ✅ Done | `intent_detector.py`, `planner.py`, `prompts.py`, `retry.py`, `clients/orchestrator_llm.py` |
| **6** | ✅ Done | LangGraph `graph.py`, `runner.py`, `main.py` CLI |
| **7** | ✅ Done | `mcp/server.py`, `mcp/registry.py` |
| **8** | ✅ Done | `test_integration_stage8.py`, `conftest.py`, retry bugfix |
| **9** | ⏳ Next | Standalone CLI demo polish |

---

## Architecture (locked)

```text
User → Ollama orchestrator (intent + summarize + explain)
         ├─ Tool 1: schema_tool      (Postgres/Mongo introspection)
         ├─ Tool 2: codegen_client   (POST /v1/chat/completions + intent)
         └─ Tool 3: execution_tool   (read-only Postgres + Mongo shell)
       → NL answer
```

**Three separate task paths** (not one forced chain):

| Intent | Tools | Execute? |
| --- | --- | --- |
| `text2sql` | schema → CodeGen(`text2sql`) | Postgres |
| `sql2nosql` | CodeGen(`sql2nosql`) | Mongo |
| `nosql2doc` | CodeGen(`nosql2doc`) | No |
| `explain_sql` | Ollama only | No |
| `validate_sql` | rules only | No |

Agent **never generates SQL** — CodeGen API does generation.

---

## Database profiles

| Profile | Env | Use |
| --- | --- | --- |
| **`standalone`** | `AGENT_DB_PROFILE=standalone` + `AGENT_DEMO_*` | Agent demos (Chinook, Northwind) |
| **`tend`** | `AGENT_DB_PROFILE=tend` + `db_id` | TEND gold / eval-aligned schemas |

**Both demo DBs loaded in Docker.** Default demo: **Chinook** (`AGENT_DEMO_DB_ID=chinook` in `agent/.env`). Switch via `--db-id northwind` or change that one env var.

| Demo | Postgres / Mongo | Questions |
| --- | --- | --- |
| **Chinook** (default) | `chinook` | `data/standalone/chinook/questions.txt` |
| **Northwind** | `northwind` | `data/standalone/northwind/questions.txt` |

Gold eval (`data/spider_gold_validation.jsonl`) — **unchanged**, uses TEND only.

---

## Initial agent `.env` (Chinook default)

Copy `agent/.env.example` → `agent/.env`:

```bash
AGENT_DB_PROFILE=standalone
AGENT_DEMO_DB_ID=chinook
AGENT_DEMO_POSTGRES_SCHEMA=public
AGENT_DEMO_SQL_DUMP=agent/data/standalone/chinook/test.sql
CODEGEN_API_URL=https://codegen-api-161349047936.asia-south2.run.app
OLLAMA_BASE_URL=http://localhost:11434
AGENT_ORCHESTRATOR_MODEL=gemma3:4b
```

MCP server: `python -m agent.mcp.server` (stdio, same tools as LangGraph).

---

## Next action

**Stage 9:** CLI demo polish + capstone walkthrough.

Run: `python agent/scripts/verify_demo_databases.py`

| Database | PG tables | PG rows (approx) | Mongo collections | Mongo docs (approx) | Agent layer |
| --- | --- | --- | --- | --- | --- |
| **chinook** | 11 | 15,607 | 11 | 15,607 | ✅ introspect + execute |
| **northwind** | 14 | 3,362 | 14 | 3,362 | ✅ introspect + execute |

**Note:** Chinook uses PascalCase table names (`"Customer"`) — schema tool must emit quoted DDL; sql2nosql Mongo collections are lowercase (`customer`).

---

## Reuse from `src/` (eval + agent aligned)

| Component | Approach |
| --- | --- |
| Prompt builders | **Import** `src.text2sql`, `src.sql2nosql`, `src.documentation` prompt builders |
| SQL validation | **Import** `src.text2sql.sql_validator` |
| CodeGen inference | **HTTP only** — Cloud Run, no local LoRA |
| DB execution | **`agent/database/`** — separate from eval execution |

Eval scripts unchanged — same `src/` modules, same gold file.

---

## Planning documents

| Doc | Contents |
| --- | --- |
| [implementation-plan.md](implementation-plan.md) | Master build plan + stages |
| [decisions.md](decisions.md) | Locked Q&A |
| [tools-plan.md](tools-plan.md) | Three MCP tools detail |
| [orchestrator-plan.md](orchestrator-plan.md) | LangGraph + intent map |
| [reuse-strategy.md](reuse-strategy.md) | Import vs separate code |
| [testing-strategy.md](testing-strategy.md) | Test plan |
| [llm-alternative.md](llm-alternative.md) | Ollama model choice |
| [overview.md](overview.md) | High-level summary |

---

## Next action

**Stage 2:** `agent/clients/codegen_client.py` with `generate_sql`, `generate_nosql`, `generate_documentation` + `src` prompt builders.
