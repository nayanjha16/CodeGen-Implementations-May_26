# Open Questions — Decisions

> Recorded from planning discussion. Source: `ai-workflow/research/open-questions/questions.md`

## Locked decisions

| ID | Decision | Notes |
| --- | --- | --- |
| **Q-1** | **A — HTTP client adapter** | `POST /v1/chat/completions` + `intent`; no changes to `codegen_api` |
| **Q-2** | All code under **`agent/`** | Nested layout per `implementation-plan.md` |
| **Q-3** | **LangGraph + Python tools first**, MCP wrapper second | See explanation below |
| **Q-4** | **Ollama** (not GPT). **gemma3:4b** after eval; qwen2.5:7b if needed | Free-form intent per `agent.md` |
| **Q-5** | **LLM orchestrator required** — not FSM-only | Matches spec §6 |
| **Q-6** | **C — Hybrid schema** | Live Postgres when Docker up; gold JSONL fallback |
| **Q-7** | **Hybrid table selection** | Keyword + FK shortlist; orchestrator refines ambiguous cases |
| **Q-8** | **B — Direct psycopg + pymongo** in `agent/database/` | Same TEND connection env; no `src/` imports for execution |
| **Q-10** | Retry prompt for **text2sql** (see below) | Same HTTP endpoint + `intent: text2sql` |
| **Q-11** | Retry on **validation and execution** failures | Both count toward max 3 |
| **Q-12** | **Full spec §1–§12** | Not text2sql-only MVP |
| **Q-13** | **Explain SQL via orchestrator LLM** | No separate explanation LoRA |
| **Q-14** | **SQL → mongo → doc** when user starts from SQL; direct nosql2doc when Mongo given | Matches training + API |
| **Q-15** | **`agent/requirements.txt`** | Separate from root ML deps |
| **Q-16** | **`tool/` reference only** | Not used in agent; Pagila was tool default, not agent default |
| **Q-17** | **Standalone demo DBs via env** | Chinook + Northwind loaded; **initial demo = Chinook**; switch with `AGENT_DEMO_*` |
| **Q-18** | **Three separate intents** | Not forced text2sql→sql2nosql→doc chain; orchestrator picks one path |
| **Q-19** | **Import prompt builders from `src/`** | Same format as eval/training; no duplicate prompt logic in agent |

## Schema table selection — phases

| Phase | Approach | When |
| --- | --- | --- |
| **Phase 1 (v1)** | **Keyword + FK + orchestrator** | Agent build now |
| **Phase 2 (optional)** | **+ Embeddings** (`BAAI/bge-small-en-v1.5` or similar) rerank on table shortlist | If wrong tables are picked **or** CPU budget allows after core agent works |

**2026-07-26 decision:** Embeddings moved to **Phase 2** — wrong table picks on **Chinook/Northwind** demos during agent testing may also trigger Phase 2.

Phase 2 embedding scope (if added):

- Embed user question + table metadata (name, columns)
- Rerank keyword/FK shortlist — does **not** replace orchestrator
- Load embedder lazily or only when `SCHEMA_USE_EMBEDDINGS=true`
- Gold eval set unchanged

## Eval complete (2026-07-25)

| Run | Folder |
| --- | --- |
| Baseline v3 | `results/spider_gold_validation_codegen-350M-multi_baseline-v3/` |
| LoRA v3 | `results/spider_gold_validation_codegen-350M-multi_lora-v3/` |

Gold dataset **unchanged** (`data/spider_gold_validation.jsonl`).

## Demo databases — decided (2026-07-26)

| ID | Status |
| --- | --- |
| **Q-9** | **Deferred** — optional BIRD db_ids via TEND later; not blocking agent |
| **Q-17** | **Done** — Chinook + Northwind standalone demos; env-driven switch |

**Initial agent demo:** Chinook (`agent/data/standalone/chinook/`).  
**Verify:** `python agent/scripts/verify_demo_databases.py`  
Gold eval unchanged.

---

## Q-10 — Retry prompt (text2sql)

On validation or execution failure, append to user message:

```text
Schema:
{schema_ddl}

Question:
{question}

Previous SQL:
{failed_sql}

Database error:
{error}

Generate corrected SQL only.
```

POST with `"intent": "text2sql"`.

---

## Q-3 — Why LangGraph first, MCP second?

**LangGraph** = Python workflow graph (nodes: schema → generate → execute → retry).

**MCP** = protocol so external clients (Cursor, Claude Desktop, etc.) can call the same tools over a standard interface.

| Build order | What you get |
| --- | --- |
| **1. LangGraph + plain Python functions** | Working agent CLI; easy to debug with breakpoints and logs |
| **2. MCP server wrapping same functions** | Capstone “MCP Tool Calling” demo without rewriting logic |

Same three tools; MCP is a **thin wrapper**, not a second implementation.

```text
Phase 1:  agent/main.py → calls tools/schema_tool.py directly
Phase 2:  mcp/server.py  → exposes extract_schema, codegen_generate, execute_query
```

---

## Q-9 — Other SQL data in Docker (for discussion)

**Current setup:** TEND Docker + gold subset (`concert_singer`, `pets_1`).

**Can you add other SQL data the same way?** Yes — options:

| Option | Effort | Notes |
| --- | --- | --- |
| **A. More TEND / Spider schemas** | Low | Run TEND `import_jsonl_tables.sh` with more JSONL rows; new `db_id` schemas in same Postgres |
| **B. Spider dev set (local files)** | Medium | Spider SQLite/JSON exists publicly; convert to TEND import format or load via custom import script |
| **C. BIRD schemas** | Medium | TEND includes BIRD; import BIRD tables into Postgres if you extend Docker setup |
| **D. Your own CSV/SQL dump** | Medium | Create schema + data in Postgres under a new `db_id`; schema tool introspects live |

**For capstone demo:** TEND gold db_ids are enough to prove the agent. **For “different data tomorrow”** testing, add one extra `db_id` via TEND import — same Docker, no new infrastructure.

**Decision deferred:** pick default `db_id` and whether to import 1–2 extra schemas beyond gold.

---

## Edge cases — plain language

These are “what if something goes wrong or weird” rules so the agent behaves predictably.

| ID | Situation | What the agent should do |
| --- | --- | --- |
| **E-1** | CodeGen API returns “please clarify task” instead of SQL | Prevent by always sending `"intent": "text2sql"` (etc.). Should not happen in normal use. |
| **E-2** | Schema tool finds **no matching tables** for the question | Don’t guess. Tell user: “I couldn’t find relevant tables — can you specify db or table names?” |
| **E-3** | SQL runs OK but **returns 0 rows** | Don’t say “here are the results.” Say clearly: “Query succeeded but returned no rows.” |
| **E-4** | Query returns **thousands of rows** | Don’t dump all into LLM summary. Return e.g. first 100 rows + “showing 100 of N.” |
| **E-5** | Orchestrator tries to call **multiple tools at once** | Run tools **one at a time** (schema → then API → then execute). Simpler and matches your spec diagram. |
| **E-6** | Ollama returns **malformed JSON** for a tool call | Validate with Pydantic; retry once or ask user to rephrase. |
| **E-7** | User asks for **Mongo doc** but only gave SQL | Graph runs sql2nosql first, then nosql2doc — state carries SQL/Mongo between steps. |

None of these change architecture — they are **behavior rules** for a reliable demo.

---

## Default edge-case limits (proposed)

- Max execution rows returned: **100**
- Max retries: **3** (Q-11)
- Empty schema: **user clarify message** (E-2)

Confirm when closing Q-9.
