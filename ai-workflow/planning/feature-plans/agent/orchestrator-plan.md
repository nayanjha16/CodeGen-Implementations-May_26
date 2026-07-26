# Orchestrator — LangGraph + Ollama (Full Spec)

> Replaces GPT-5.5 from `agent.md` §14. See [llm-alternative.md](llm-alternative.md).

## Agent responsibilities (spec §6)

| Responsibility | Module |
| --- | --- |
| Intent detection | `agent/intent_detector.py` |
| Planning | `agent/planner.py` |
| Tool selection | LangGraph + planner map |
| Tool orchestration | `agent/main.py` (graph) |
| Retry | `agent/retry.py` |
| Response formatting | graph `summarize` node |

**Never generates SQL** — only calls `tools/fastapi_tool.py`.

## System prompt (spec §11)

Stored in `agent/prompts.py`:

```text
You are an AI Database Agent.

Never generate SQL directly.
Always use tools.

Workflow:
1. Detect intent.
2. Retrieve relevant schema.
3. Call the Capstone API.
4. Execute generated query if requested.
5. If execution fails, retry by passing the error back to the model.
6. Return natural language results.

Never assume table names.
Never hallucinate schemas.
```

Bound to Ollama orchestrator model as system message.

## LangGraph workflow (spec §8)

```text
START
  → detect_intent
  → plan_tools              # planner.py: intent → ordered tool list
  → extract_schema            # if plan requires
  → validate_query            # if SQL execution path
  → codegen_generate          # fastapi_tool by intent
  → execute_query             # postgres and/or mongo
  → check_result
       ├─ ok → summarize
       └─ fail → retry (≤3) → codegen_generate with error
  → END
```

## Intent → plan map (`planner.py`)

**Separate paths** — orchestrator runs **one** intent per user request unless user explicitly asks for a multi-step flow.

| Intent | Steps |
| --- | --- |
| `text2sql` | schema → generate_sql → validate → execute_postgres → summarize |
| `sql2nosql` | generate_nosql → execute_mongo → summarize |
| `nosql2doc` | generate_documentation → summarize |
| `explain_sql` | schema (optional) → ollama_explain → summarize |
| `validate_sql` | validate only → summarize |

**Initial demo DB:** Chinook (`AGENT_DB_PROFILE=standalone`). Switch to Northwind via `AGENT_DEMO_*` env — see `agent/data/standalone/README.md`.

## Orchestrator LLM usage

| Node | Ollama? | CodeGen API? |
| --- | --- | --- |
| detect_intent | ✅ (or rules + LLM fallback) | ❌ |
| plan_tools | ✅ or deterministic map | ❌ |
| summarize (FR-6) | ✅ | ❌ |
| explain_sql | ✅ | ❌ |
| generate_sql/nosql/doc | ❌ | ✅ |

**Recommended model:** `qwen2.5:7b-instruct` or `gemma3:4b` (already on your machine).

## Standalone agent (not Cursor)

Entry: `agent/main.py`

```powershell
python -m agent.main "How many singers are from France?" --db-id concert_singer
python -m agent.main --intent sql2nosql --sql "SELECT ..."
```

MCP server: `python -m mcp.server` for capstone MCP demo.

## Memory (spec §13 Phase 4)

Not in initial build — single-turn first. Structure allows adding memory node later.
