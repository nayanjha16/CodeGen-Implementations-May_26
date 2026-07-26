# Stage 5 — Orchestrator (Ollama)

**Date:** 2026-07-25  
**Status:** Complete  
**Plan:** [database-agent-plan.md](../../planning/feature-plans/database-agent-plan.md) Stage 5

## Implemented

- [x] `agent/orchestrator/intent_detector.py` — text2sql, sql2nosql, nosql2doc, explain_sql, validate_sql
- [x] `agent/orchestrator/planner.py` — intent → tool chain map
- [x] `agent/orchestrator/prompts.py` — system prompt (spec §11)
- [x] `agent/orchestrator/retry.py` — max 3 attempts with error context to CodeGen
- [x] `agent/clients/orchestrator_llm.py` — Ollama `/api/chat`
- [x] `agent/tests/test_orchestrator_stage5.py`

## Intent → tool chains

| Intent | Chain |
|--------|-------|
| text2sql | schema → CodeGen → execute Postgres |
| sql2nosql | CodeGen → execute Mongo |
| nosql2doc | CodeGen only |
| explain_sql | Ollama only |
| validate_sql | rules only |

## Assumptions

- Default model: `gemma3:4b` via `AGENT_ORCHESTRATOR_MODEL`
- CodeGen `intent` is set separately from orchestrator intent classification

## Blockers

None.

## Next (Stage 6)

LangGraph graph + CLI entry.
