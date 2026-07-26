# Risk Analysis — AI Database Agent (`database-agent`)

> **Research date:** 2026-07-19  
> **Feature:** `database-agent`

## 1. Architectural Risks

| Risk | Severity | Description | Mitigation (planning) |
|------|----------|-------------|------------------------|
| **A-1 API contract mismatch** | High | Spec documents `/generate/*`; deployed API is OpenAI `/v1/chat/completions` | Adapter in `fastapi_tool.py`; document mapping; optional thin shim routes later |
| **A-2 Dual intent systems** | Medium | Agent detects user intent; FastAPI has its own classifier | Agent passes `intent` override on every Capstone call |
| **A-3 Orchestrator vs fine-tuned model confusion** | High | Reviewers may think FastAPI classifier = "the agent" | Clear architecture diagram; agent never calls `sql_generator.py` locally |
| **A-4 MCP ceremony without value** | Low | MCP layer adds complexity if only LangGraph uses tools | Thin MCP server delegating to same Python functions |
| **A-5 Monolith creep** | Medium | Putting inference back into agent process | Enforce HTTP-only inference rule (IR-8) |

## 2. Integration Risks

| Risk | Severity | Description | Mitigation |
|------|----------|-------------|------------|
| **I-1 Cloud Run cold start** | High | 1–3+ min model load on first request | Warm `/health` before demo; document in runbook |
| **I-2 Cloud Run scale-to-zero** | Medium | Demo fails if service asleep | Option 1 from `fastapi-deploy/README.md` (auto sleep OK with warm-up) |
| **I-3 TEND dependency** | High | `database_execution.py` imports external TEND repo; default path macOS | Set `TEND_REPO_PATH` on Windows; or direct psycopg in execution tool |
| **I-4 Missing `tool/` codebase** | High | text2sql-ui-tool modules documented but not on disk | Re-implement schema loader/client in `tools/`; don't assume `tool/` imports |
| **I-5 SQL extraction from LLM output** | Medium | Model may return prose + SQL | Reuse extraction patterns from `sql_generator.py` / API post-processing |
| **I-6 nosql2doc vs SQL documentation** | Medium | Spec capability doesn't match adapter task | MVP text2sql only; document naming mismatch for doc path |

## 3. Security & Safety Risks

| Risk | Severity | Description | Mitigation |
|------|----------|-------------|------------|
| **S-1 Arbitrary SQL execution** | Critical | Agent executes generated SQL against real DB | Read-only gate (SELECT/WITH only); row limits |
| **S-2 Prompt injection via user question** | Medium | User text flows to model and logs | Sanitize logs; system prompt boundaries |
| **S-3 Cloud Run public URL** | Medium | Unauthenticated inference endpoint | Accept for capstone; API key optional later |
| **S-4 Secrets in config** | Medium | DB passwords, OpenAI keys | `.env` gitignored; `config/settings.py` pattern |
| **S-5 Error messages leak schema** | Low | Retry loop sends DB errors to model | Accept for self-correction; truncate in user-facing summary |

## 4. Operational Risks

| Risk | Severity | Description | Mitigation |
|------|----------|-------------|------------|
| **O-1 Orchestrator LLM cost** | Medium | Every agent turn + retries = multiple LLM calls | Use cheap model; cache schema; limit retries to 3 |
| **O-2 Dual LLM stack** | Medium | Orchestrator (GPT) + CodeGen (Cloud Run) | Required by architecture; budget accordingly |
| **O-3 No agent monitoring** | Low | Spec mentions LangSmith optional | Structured logs minimum for capstone |
| **O-4 Dependency sprawl** | Medium | LangGraph + MCP + httpx + psycopg new deps | Separate `agent/requirements.txt` or section in root |

## 5. Technical Debt & Existing Gaps

| Item | Location | Impact on agent |
|------|----------|-----------------|
| Stale research docs | Older `project-summary` LoRA-only narrative | **Resolved** — research updated 2026-07-19 |
| text2sql-ui-tool without `tool/` | ai-workflow says complete | Cannot reuse; reimplement or restore from backup |
| hf-deploy removed | — | Use `fastapi-deploy` only |
| Classifier `clarify` at low confidence | `codegen_api` | Agent must force intent |
| v2 baseline metrics incomplete EX in JSON | `baseline-v2/metrics.json` | Unrelated to agent; don't block |
| TEND default path | `database_execution.py` | Breaks on Windows without env |

## 6. Scalability Concerns

| Concern | Notes |
|---------|-------|
| Schema tool v1 keyword search | Won't scale to large warehouses; OK for capstone |
| Full schema in prompt | Token limits; schema tool subset is required |
| Synchronous agent loop | OK for demo; async/streaming later |
| Single Cloud Run instance | `max-instances=1` in deploy config |

## 7. Missing Validations

| Validation | Needed for |
|------------|------------|
| Agent never emits raw SQL without tool call | FR-6 / spec §6 |
| Retry count enforced | FR-5 |
| Read-only SQL enforcement | Safety |
| Schema tool returns non-empty subset | FR-2 |
| Capstone tool handles API 5xx / timeout | Resilience |
| E2E with mocked Cloud Run + mocked DB | CI without GPU/network |

## 8. Risk Priority for Planning

**Must address in plan (P0):**

- A-1 API adapter strategy
- I-1 Cloud Run warm-up
- I-3 Execution backend (TEND vs direct psycopg)
- S-1 Read-only SQL
- I-4 Rebuild schema + client tools

**Address in implementation (P1):**

- A-2 Explicit intent override
- I-5 SQL extraction
- O-1 Orchestrator model choice

**Document only (P2):**

- I-6 nosql2doc naming
- A-4 MCP thin wrapper

## 9. Risk Acceptance (capstone scope)

Accept for MVP:

- No human-in-the-loop approval before SQL execution
- No conversation memory
- Keyword-based schema tool (not vector search)
- Single Postgres database
- Public Cloud Run endpoint

Not acceptable:

- Agent generating SQL directly in orchestrator prompt without tool
- Unrestricted DML/DDL execution
