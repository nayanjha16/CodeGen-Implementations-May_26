# Architecture Map — AI Database Agent (`database-agent`)

> **Research date:** 2026-07-19 · **Implementation complete:** 2026-07-26  
> **Spec:** `agent/doc/agent.md`  
> **Deployed API:** `fastapi-deploy/codegen_api` → Cloud Run

## 1. Target System (from spec)

```
┌─────────────────────────────────────────────────────────────────┐
│                         User / Client                            │
└───────────────────────────────┬─────────────────────────────────┘
                                │ natural language
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  AI Agent (LangGraph)                                            │
│  • Intent detection    • Planning    • Tool selection            │
│  • Retry orchestration • NL summarization                        │
│  • NEVER generates SQL directly                                  │
└───┬─────────────────┬─────────────────────┬───────────────────┘
    │                 │                     │
    ▼                 ▼                     ▼
┌─────────────┐ ┌──────────────────┐ ┌─────────────────────────┐
│ Schema Tool │ │ CodeGen API Tool │ │ Execution Tool          │
│ (MCP #1)    │ │ (MCP #2)         │ │ (MCP #3)                │
│             │ │ HTTP → FastAPI   │ │ Postgres / Mongo        │
└─────────────┘ └────────┬─────────┘ └───────────┬─────────────┘
                         │                         │
                         ▼                         ▼
              ┌────────────────────┐    ┌─────────────────────┐
              │ codegen_api        │    │ TEND or direct DB   │
              │ (Cloud Run)        │    │ drivers             │
              │ LoRA v3 adapters   │    │                     │
              └────────────────────┘    └─────────────────────┘
```

## 2. Current System (what exists today)

```
┌──────────────┐     HTTP (optional)      ┌─────────────────────────────┐
│ Cursor /     │ ───────────────────────► │ fastapi-deploy/codegen_api  │
│ manual client│   POST /v1/chat/        │ • IntentClassifier          │
└──────────────┘   completions           │ • MultiAdapterRouter (PEFT) │
                                         │ • GET /health, /v1/models   │
                                         └──────────────┬──────────────┘
                                                        │
                        Hugging Face Hub                │
                        codegenstudio LoRA v3           │
                                                        ▼
                                         ┌─────────────────────────────┐
                                         │ Salesforce/codegen-350M-multi│
                                         │ + task adapters              │
                                         └─────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ src/ (offline training & eval — not wired to agent)                  │
│  text2sql/  sql2nosql/  documentation/  evaluation/  training/     │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ eval only
                                ▼
                    ┌───────────────────────┐
                    │ TEND (external repo)     │
                    │ Postgres + Mongo         │
                    │ via database_execution.py│
                    └───────────────────────┘
```

**Gap (resolved 2026-07-26):** Full path implemented in `agent/` — user question → schema tool → LangGraph → CodeGen API → execution → NL response. See `agent/orchestration/runner.py`.

## 3. Module Relationships

### 3.1 Spec modules (`agent.md` §12) — implemented under `agent/`

| Spec path | Status | Notes |
|-----------|--------|-------|
| `main.py`, `orchestrator/planner.py`, `prompts.py`, `intent_detector.py`, `retry.py` | ✅ | Under `agent/orchestrator/` + `agent/main.py` |
| `mcp/server.py`, `registry.py` | ✅ | stdio MCP |
| `tools/schema_tool.py`, `fastapi_tool.py`, `execution_tool.py` | ✅ | Three MCP tools |
| `codegen_api` (CodeGen API) | ✅ | `fastapi-deploy/codegen_api` — HTTP client only |
| `database/postgres.py`, `mongodb.py` | ✅ | Read-only execution + introspection |
| `config/settings.py` | ✅ | `agent/config/settings.py` |
| `web/` (agent Web UI) | ✅ | FastAPI chat UI |
| `tests/` | ✅ | 88 tests |

### 3.2 Reusable `src/` modules

| Module | Path | Reuse for agent |
|--------|------|-----------------|
| Text2SQL prompts | `src/text2sql/prompt_builder.py`, `sql_executor.py` | Build CodeGen API payloads |
| SQL validation | `src/text2sql/sql_validator.py` | Pre/post execution safety |
| SQL2NoSQL | `src/sql2nosql/nosql_generator.py`, `prompt_builder.py` | Stage 2 agent path |
| Documentation | `src/documentation/doc_generator.py` | Stage 3 agent path |
| Schema conversion | `src/utils/schema_conversion.py` | Format schema for prompts |
| Dataset schemas | `src/datasets/tend_loader.py` | Static schema source for demos |
| DB execution | `src/evaluation/database_execution.py` | Pattern for execution tool |
| Config | `src/utils/config.py`, `paths.py` | Conventions for agent config |

### 3.3 Deployed inference service

| Component | Path | Role |
|-----------|------|------|
| FastAPI app | `fastapi-deploy/codegen_api/api/app.py` | HTTP gateway |
| Schemas | `fastapi-deploy/codegen_api/api/schemas.py` | OpenAI-compatible models; optional `intent` override |
| Router | `fastapi-deploy/codegen_api/adapters/router.py` | Load base + hot-swap LoRA |
| Classifier | `fastapi-deploy/codegen_api/classifier/classifier.py` | Rules + embeddings; not agent-level |
| Prompt | `fastapi-deploy/codegen_api/prompt/builder.py` | Prepends `Task: <intent>` |
| Manifest | `fastapi-deploy/manifest.yaml` | v3 adapters, generation params |
| Deploy | `fastapi-deploy/infra/cloudrun/deploy.py` | Cloud Run URL in `deploy.env` |

## 4. Service Boundaries

| Boundary | Owner | Contract |
|----------|-------|----------|
| Agent ↔ Orchestrator LLM | New `agent/` | Tool calls / LangGraph state |
| Agent ↔ MCP | New `mcp/` | MCP tool schemas |
| Agent codegen client ↔ Cloud Run | `agent/clients/codegen_client.py` | HTTP JSON → `/v1/chat/completions` |
| Execution tool ↔ DB | New `tools/execution_tool.py` | `{"query"}` → `{"rows", "error"}` |
| Schema tool ↔ metadata | New `tools/schema_tool.py` | `{"question"}` → `{tables, columns, relationships}` |
| Model inference | `codegen_api` (unchanged) | No SQL generation inside agent |

## 5. Data Flow — Text2SQL MVP (target)

```
1. User: "Show top 10 customers by revenue"
2. Agent: intent = text2sql
3. Schema Tool:
     input: question
     output: { tables: [customers, orders], columns: [...], relationships: [...] }
4. CodeGen API (Cloud Run):
     POST /v1/chat/completions
     body: { model: "codegen-text2sql", intent: "text2sql",
             messages: [{ role: "user", content: "<question>\n\nSchema:\n<ddl>" }] }
     output: SQL string (extracted from assistant message)
5. Execution Tool:
     input: SQL
     output: { rows: [...] } or { error: "..." }
6. If error and retries < 3:
     CodeGen API with prior SQL + error in prompt → corrected SQL → goto 5
7. Agent: summarize rows → user
```

## 6. Dependency Graph (implementation order)

```
config/settings.py
    ├── tools/fastapi_tool.py ──► Cloud Run (codegen_api)
    ├── tools/schema_tool.py
    └── tools/execution_tool.py ──► TEND or psycopg

tools/* ──► mcp/registry.py ──► mcp/server.py

agent/prompts.py, intent_detector.py
    └── agent/planner.py (LangGraph)
            └── agent/retry.py
                    └── agent/main.py (CLI/API entry)

tests/ (unit + E2E)
```

## 7. External Dependencies

| Dependency | Required for | Notes |
|------------|--------------|-------|
| Cloud Run `codegen-api` | AI Database Agent | Cold start 1–3 min; URL in `deploy.env` |
| TEND repo | Execution (eval pattern) | `TEND_REPO_PATH`; default path is macOS-centric |
| Hugging Face Hub | Cloud Run adapter load | `codegenstudio/*-lora` public |
| Orchestrator LLM | Agent | **Ollama** (`gemma3:4b`) via `agent/clients/orchestrator_llm.py` |
| LangGraph | Agent planner | **`agent/orchestration/graph.py`** — in `agent/requirements.txt` |
| MCP SDK | MCP server | **`agent/mcp/server.py`** — in `agent/requirements.txt` |

## 8. Inconsistencies (spec vs codebase)

| Topic | Spec | Codebase |
|-------|------|----------|
| API routes | `/generate/sql`, `/generate/nosql`, … | `/v1/chat/completions` only |
| Package name | `capstone_api` | `codegen_api` |
| SQL explanation | `/generate/explanation` | **Ollama orchestrator** in agent (`explain_sql` intent) — no separate API route |
| Schema in API | JSON `{question, schema}` body | Schema embedded in user message string |
| Agent intent | Agent detects | FastAPI has internal classifier (+ optional `intent` override) |
| Documentation task | SQL docs | `nosql2doc` — Mongo query documentation |

Planning documented gaps as **adapter shims** (see `database-agent-plan.md` AD-1).
