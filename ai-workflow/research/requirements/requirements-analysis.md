# Requirements Analysis — AI Database Agent (`database-agent`)

> **Research date:** 2026-07-19  
> **Sources:** `agent/doc/agent.md`, `fastapi-deploy/`, `src/`  
> **Implementation:** Complete (2026-07-26) — see `validation/validation-reports/database-agent-validation.md`

## 1. Functional Requirements (from spec)

| ID | Requirement | Description | Status | Evidence |
|----|-------------|-------------|--------|----------|
| **FR-1** | User query | Accept NL question; determine intent (e.g. Text2SQL) | ✅ | `agent/orchestrator/intent_detector.py` + Ollama `gemma3:4b` |
| **FR-2** | Schema extraction | Call Schema Tool; return relevant tables/columns/relationships only | ✅ | `agent/tools/schema_tool.py` (keyword match on introspected metadata) |
| **FR-3** | Query generation | Call Cloud Run CodeGen API with question + schema | ✅ | `agent/clients/codegen_client.py` → `/v1/chat/completions` |
| **FR-4** | Query execution | Call Execution Tool; return rows | ✅ | `agent/tools/execution_tool.py` (Postgres + Mongo) |
| **FR-5** | Error recovery | On execution failure, retry via FastAPI with error (max 3) | ✅ | `agent/orchestrator/retry.py` |
| **FR-6** | NL response | Summarize results for user | ✅ | Ollama summarize + deterministic listing path |

## 2. Supported Capabilities (from spec §5)

| Capability | Spec flow | Implementation status |
|------------|-----------|---------------------|
| Text → SQL | Question → SQL | ✅ LangGraph path + Cloud Run `text2sql` intent |
| SQL → MongoDB | SQL → Mongo aggregation | ✅ `sql2nosql` intent + execution on Mongo |
| SQL documentation | SQL → business explanation | ✅ `nosql2doc` intent (Mongo query docs via API) |
| Explain SQL | SQL → step-by-step | ✅ Ollama orchestrator (`explain_sql` intent) — not a CodeGen API route |
| Query validation | Syntax, tables, joins, unsafe queries | ✅ `agent/tools/validation_tool.py` wraps `src/text2sql/sql_validator.py` |

## 3. Agent Responsibilities (from spec §6)

| Responsibility | Required | Status |
|----------------|----------|--------|
| Intent detection | Agent-level (user goal) | ✅ |
| Planning | Multi-step tool plan | ✅ `agent/orchestrator/planner.py` |
| Tool selection | MCP tools | ✅ LangGraph + MCP registry |
| Tool orchestration | Ordered calls + state | ✅ `agent/orchestration/graph.py` |
| Retry | Max 3 on execution failure | ✅ |
| Response formatting | NL summary | ✅ |
| **Never generate SQL** | Orchestrator must not write SQL | ✅ CodeGen API only |

## 4. MCP Tools (from spec §7)

| Tool | Input | Output | Status |
|------|-------|--------|--------|
| **Schema Extraction** | `{ "question": "..." }` | `{ tables, columns, relationships }` | ✅ `schema_tool` |
| **Cloud Run CodeGen API** | OpenAI `/v1/chat/completions` | SQL / NoSQL / doc text | ✅ `fastapi_tool` → `fastapi-deploy/codegen_api` |
| **Execution** | `{ "query": "..." }` | `{ "rows": [] }` | ✅ `execution_tool` |

### CodeGen API — spec vs deployed

The agent spec (§10) documents convenience routes; **production uses OpenAI-compatible chat only**. The agent adapter maps spec intents to HTTP calls.

| Spec endpoint | Deployed route | Agent mapping |
|---------------|----------------|---------------|
| `POST /generate/sql` | `POST /v1/chat/completions` | `intent: "text2sql"` or `model: "codegen-text2sql"` |
| `POST /generate/nosql` | same | `intent: "sql2nosql"` |
| `POST /generate/documentation` | same | `intent: "nosql2doc"` |
| `POST /generate/explanation` | — | **Ollama orchestrator** (`explain_sql`) — no CodeGen route |
| `GET /health` | `GET /health` | ✅ |

## 5. Reusable repo features (agent integration)

| Feature | Location | Agent reuse |
|---------|----------|-------------|
| LoRA multi-adapter inference | `codegen_api/adapters/router.py` | Via HTTP only |
| Intent classification (task) | `codegen_api/classifier/` | Agent passes explicit `intent` to avoid `clarify` |
| OpenAI-compatible API | `codegen_api/api/app.py` | Agent HTTP transport |
| Prompt `Task:` prefix | `codegen_api/prompt/builder.py` | Automatic when using API |
| SQL validation | `src/text2sql/sql_validator.py` | Validation tool pre-check |
| TEND Postgres/Mongo execution | `src/evaluation/database_execution.py` | Execution tool backend |
| Schema text conversion | `src/utils/schema_conversion.py` | Schema tool output formatting |
| Gold validation dataset | `data/spider_gold_validation.jsonl` | Demo schemas + questions |
| Cloud Run deployment | `fastapi-deploy/codegen_api` | Production CodeGen API URL |

## 6. Delivered MVP (Stages 1–10)

| Item | Location | Status |
|------|----------|--------|
| Agent config | `agent/config/settings.py`, `agent/.env` | ✅ |
| Schema tool | `agent/tools/schema_tool.py` | ✅ |
| CodeGen client tool | `agent/tools/fastapi_tool.py` | ✅ |
| Execution tool | `agent/tools/execution_tool.py` | ✅ |
| LangGraph agent | `agent/orchestration/graph.py` | ✅ |
| MCP server | `agent/mcp/server.py` | ✅ |
| CLI entry | `agent/main.py` | ✅ |
| Web UI | `agent/web/` | ✅ Stage 10 |
| Tests | `agent/tests/` — **88 passed** | ✅ |

### Post-MVP (future)

| Feature | Priority |
|---------|----------|
| Vector schema search (spec Phase 3) | Future |
| Conversation memory (Phase 4) | Future |
| Human approval before execute (Phase 5) | Future |
| Query optimization (Phase 6) | Future |
| Multi-database beyond Chinook/Northwind | Future |

## 7. Inferred Requirements (implemented)

| ID | Requirement | Evidence |
|----|-------------|----------|
| IR-1 | Agent passes **explicit `intent`** to Cloud Run | `codegen_client.py` |
| IR-2 | Schema embedded in user message for API | Prompt builder in client |
| IR-3 | Read-only SQL enforcement before execution | Validation + execution guards |
| IR-4 | Configurable `CODEGEN_API_URL` | `agent/.env` |
| IR-5 | Structured logging per agent step | Runner + graph logging |
| IR-6 | Timeouts on HTTP and DB calls | Client + DB settings |
| IR-7 | Windows-compatible `TEND_REPO_PATH` | Demo scripts + docs |
| IR-8 | No torch/transformers in agent | Inference via HTTP only |

## 8. Constraints (still relevant)

| Constraint | Impact |
|------------|--------|
| Cloud Run cold start | First request slow; health ping before demo |
| Small model (350M) | Quality limits; retry loop helps FR-5 |
| Orchestrator needs local Ollama | `gemma3:4b` for intent + NL summary |
| LoRA v3 eval (n=50) | Separate from agent demo quality |

## 9. Requirements Traceability Matrix

| Spec section | Implementation |
|--------------|----------------|
| FR-1–FR-6 | `agent/orchestration/`, `agent/orchestrator/` |
| §7 Tool 1 | `agent/tools/schema_tool.py` |
| §7 Tool 2 | `agent/tools/fastapi_tool.py` |
| §7 Tool 3 | `agent/tools/execution_tool.py` |
| §8 Workflow | `agent/orchestration/graph.py` |
| §10 FastAPI | Adapter in `fastapi_tool.py` → `/v1/chat/completions` |
| §11 Agent prompt | `agent/orchestrator/prompts.py` |
| §12 Structure | `agent/` tree (see `agent/README.md`) |

## 10. Acceptance Criteria — **met**

1. ✅ User can ask a NL question via CLI or Web UI against configured Postgres/Mongo.
2. ✅ Agent calls schema tool → CodeGen API (Cloud Run) → execution tool without generating SQL in the orchestrator.
3. ✅ On invalid SQL, agent retries with error feedback, up to 3 attempts.
4. ✅ User receives a natural-language answer referencing query results.
5. ✅ Three tools registered on MCP server and invocable externally.
6. ✅ pytest: 88 tests including mocked E2E and live integration (Docker).
