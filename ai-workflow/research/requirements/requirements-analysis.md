# Requirements Analysis — AI Database Agent (`database-agent`)

> **Research date:** 2026-07-19  
> **Sources:** `agent/doc/agent.md`, `fastapi-deploy/`, `src/`, `ai-workflow/planning/feature-plans/text2sql-ui-tool-plan.md`

## 1. Functional Requirements (from spec)

| ID | Requirement | Description | Status | Evidence / gap |
|----|-------------|-------------|--------|----------------|
| **FR-1** | User query | Accept NL question; determine intent (e.g. Text2SQL) | ❌ Missing | No agent; FastAPI classifier is task-routing not user-facing intent |
| **FR-2** | Schema extraction | Call Schema Tool; return relevant tables/columns/relationships only | ❌ Missing | No schema tool; `schema_conversion.py` formats static text only |
| **FR-3** | Query generation | Call Capstone FastAPI with question + schema | ⚠️ Partial | Cloud Run `/v1/chat/completions` works; no agent client; routes differ from spec |
| **FR-4** | Query execution | Call Execution Tool; return rows | ⚠️ Partial | TEND execution in eval only; no `{query}→{rows}` agent API |
| **FR-5** | Error recovery | On execution failure, retry via FastAPI with error (max 3) | ❌ Missing | No retry loop anywhere |
| **FR-6** | NL response | Summarize results for user | ❌ Missing | No orchestrator LLM |

## 2. Supported Capabilities (from spec §5)

| Capability | Spec flow | Implementation status |
|------------|-----------|---------------------|
| Text → SQL | Question → SQL | ✅ Model + API (`text2sql` intent); ❌ agent orchestration |
| SQL → MongoDB | SQL → Mongo aggregation | ✅ Model + API (`sql2nosql`); ❌ agent orchestration |
| SQL documentation | SQL → business explanation | ⚠️ Spec says SQL docs; API has `nosql2doc` (Mongo query docs) |
| Explain SQL | SQL → step-by-step | ❌ Not in API or `src/` |
| Query validation | Syntax, tables, joins, unsafe queries | ⚠️ `SQLValidator` in `src/text2sql/sql_validator.py` (local); not exposed as agent tool |

## 3. Agent Responsibilities (from spec §6)

| Responsibility | Required | Status |
|----------------|----------|--------|
| Intent detection | Agent-level (user goal) | ❌ |
| Planning | Multi-step tool plan | ❌ |
| Tool selection | MCP tools | ❌ |
| Tool orchestration | Ordered calls + state | ❌ |
| Retry | Max 3 on execution failure | ❌ |
| Response formatting | NL summary | ❌ |
| **Never generate SQL** | Orchestrator must not write SQL | N/A until agent exists |

## 4. MCP Tools (from spec §7)

| Tool | Input | Output | Status |
|------|-------|--------|--------|
| **Schema Extraction** | `{ "question": "..." }` | `{ tables, columns, relationships }` | ❌ Missing |
| **Capstone FastAPI** | Spec: per-route JSON | SQL / NoSQL / doc text | ⚠️ Service exists; tool wrapper missing |
| **Execution** | `{ "query": "..." }` | `{ "rows": [] }` | ❌ Missing agent-facing tool |

### Capstone API endpoints — spec vs implemented

| Spec endpoint | Implemented | Mapping |
|---------------|-------------|---------|
| `POST /generate/sql` | ❌ | Use `POST /v1/chat/completions` + `intent: "text2sql"` or `model: "codegen-text2sql"` |
| `POST /generate/nosql` | ❌ | Same with `sql2nosql` |
| `POST /generate/documentation` | ❌ | Same with `nosql2doc` |
| `POST /generate/explanation` | ❌ | **Gap** — defer or add new adapter/task |
| `GET /health` | ✅ `/health` | Ready |

## 5. Implemented Features (reusable, not agent)

| Feature | Location | Agent reuse |
|---------|----------|-------------|
| LoRA multi-adapter inference | `codegen_api/adapters/router.py` | Via HTTP only |
| Intent classification (task) | `codegen_api/classifier/` | Agent should pass explicit `intent` to avoid `clarify` |
| OpenAI-compatible API | `codegen_api/api/app.py` | Capstone tool transport |
| Prompt `Task:` prefix | `codegen_api/prompt/builder.py` | Automatic when using API |
| SQL generation (local) | `src/text2sql/sql_generator.py` | Do **not** use in agent — use API |
| SQL validation | `src/text2sql/sql_validator.py` | Execution tool pre-check |
| SQLite execution (eval) | `src/text2sql/sql_executor.py` | Different from Postgres agent path |
| TEND Postgres/Mongo execution | `src/evaluation/database_execution.py` | Execution tool backend candidate |
| Schema text conversion | `src/utils/schema_conversion.py` | Schema tool output formatting |
| Gold validation dataset | `data/spider_gold_validation.jsonl` | Demo schemas + questions |
| Cloud Run deployment | `fastapi-deploy/` | Production Capstone API URL |
| Classifier tests | `fastapi-deploy/tests/test_classifier.py` | Unrelated to agent tests |

## 6. Missing Features (must build for MVP)

### MVP (capstone demo — Text2SQL path)

1. **Agent config** — API URL, DB connection, max retries, orchestrator LLM keys
2. **Schema tool v1** — Return relevant subset (keyword/table match or embedding — TBD in planning)
3. **FastAPI client tool** — HTTP wrapper around `/v1/chat/completions` + SQL extraction
4. **Execution tool** — Run read-only SQL against Postgres; return rows + errors
5. **LangGraph agent** — Tool-calling graph: schema → generate → execute → retry → summarize
6. **MCP server** — Expose the three tools (can be thin wrapper over Python functions)
7. **Entry point** — CLI or small FastAPI for demo (`agent/main.py`)
8. **Tests** — Unit tests per tool + one E2E scenario from `agent.md`

### Post-MVP (spec §5 / Phase 2+)

| Feature | Priority |
|---------|----------|
| SQL → Mongo agent path | High (second demo) |
| Mongo documentation path | Medium |
| Explain SQL | Low (not in current API) |
| Vector schema search (spec Phase 3) | Future |
| Conversation memory (Phase 4) | Future |
| Human approval before execute (Phase 5) | Future |
| Query optimization (Phase 6) | Future |
| Multi-database (Phase 2) | Future |

## 7. Inferred Requirements (not explicit in spec)

| ID | Requirement | Rationale |
|----|-------------|-----------|
| IR-1 | Agent must pass **explicit `intent`** to Cloud Run | Avoid low-confidence `clarify` responses |
| IR-2 | Schema must be embedded in user message for API | API has no separate schema field |
| IR-3 | Read-only SQL enforcement before execution | Safety for demo DB |
| IR-4 | Configurable `CODEGEN_API_URL` | Local vs Cloud Run |
| IR-5 | Structured logging per agent step | Capstone demo + debugging |
| IR-6 | Timeouts on HTTP and DB calls | Cloud Run cold start + hung queries |
| IR-7 | Windows-compatible `TEND_REPO_PATH` | User on Windows; default path is macOS |
| IR-8 | Do not bundle torch/transformers in agent | Inference only via HTTP |

## 8. Constraints

| Constraint | Impact |
|------------|--------|
| Capstone timeline | MVP = text2sql path first |
| Cloud Run cold start | First request slow; health ping before demo |
| Small model (350M) | Quality limits; retry loop helps FR-5 |
| No `tool/` on disk | Cannot import planned UI modules; rebuild schema/client |
| Agent must use MCP (spec) | MCP server required for grading narrative |
| Orchestrator needs tool-calling LLM | Additional API cost vs local-only stack |
| v1 eval at n=5 only | Agent quality separate from v1 metrics |
| v3 full eval later | Do not block agent on n=50 re-run |

## 9. Requirements Traceability Matrix (planning input)

| Spec section | Planning epic |
|--------------|---------------|
| FR-1–FR-6 | Agent core + LangGraph |
| §7 Tool 1 | Schema tool |
| §7 Tool 2 | FastAPI client tool |
| §7 Tool 3 | Execution tool |
| §8 Workflow | Planner graph edges |
| §10 FastAPI | Adapter layer decision |
| §11 Agent prompt | `agent/prompts.py` |
| §12 Structure | Repo layout under `agent/`, `tools/`, `mcp/` |

## 10. Acceptance Criteria (draft for planning)

**MVP done when:**

1. User can ask a NL question via CLI against a configured Postgres database.
2. Agent calls schema tool → Capstone API (Cloud Run) → execution tool without generating SQL in the orchestrator.
3. On invalid SQL, agent retries at least once with error feedback, up to 3 attempts.
4. User receives a natural-language answer referencing query results.
5. Three tools are registered on an MCP server and invocable externally.
6. pytest covers tools and at least one mocked E2E agent path.
