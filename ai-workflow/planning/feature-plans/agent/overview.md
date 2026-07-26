# Agent Layer — Overview

> **Source of truth:** [../../../../agent/doc/agent.md](../../../../agent/doc/agent.md) — full specification, unchanged.

## What the agent is (from your spec)

An **orchestrator** that:

1. Understands user intent (FR-1)
2. Retrieves **only relevant schema** (FR-2)
3. Calls the **Capstone FastAPI / CodeGen API** for generation (FR-3)
4. **Executes** SQL or Mongo (FR-4)
5. **Retries** up to 3 times on failure (FR-5)
6. Returns a **natural language** answer (FR-6)

The agent **never generates SQL**. Your fine-tuned LoRA models do that through the HTTP API.

## Two LLMs — different jobs

```text
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATOR (Ollama — replaces GPT-5 in spec §14)          │
│  Intent · planning · summarize · explain SQL in English      │
└───────────────────────────┬─────────────────────────────────┘
                            │ calls tools
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  CODEGEN API (Cloud Run — your Kaggle-trained LoRA)          │
│  POST /v1/chat/completions + intent → SQL / Mongo / docs     │
└─────────────────────────────────────────────────────────────┘
```

Your curl flow is **Tool 2** inside the agent — unchanged:

```json
{
  "model": "codegen-text2sql",
  "intent": "text2sql",
  "messages": [{ "role": "user", "content": "Schema:\n...\n\nQuestion:\n..." }]
}
```

## Full capabilities (spec §5) — all in initial build

| Capability | Tools used |
| --- | --- |
| Text → SQL | Schema → CodeGen (`text2sql`) → Postgres |
| SQL → MongoDB | CodeGen (`sql2nosql`) → Mongo |
| SQL documentation | CodeGen (`nosql2doc`) |
| Explain SQL | Ollama orchestrator (NL only, no new query) |
| Query validation | Rule-based `lib/sql_validation.py` before execute |

## Testing on different data

Adapters generalize when:

- Schema tool returns correct DDL
- CodeGen gets the same prompt shape as training
- Execution DB matches that schema

Gold eval measures adapters; the agent adds schema extraction + HTTP + execution + retry on **any** question.

## Demo databases (2026-07-26)

**Initial standalone demo:** **Chinook** — copy `agent/.env.example` → `agent/.env` (default `AGENT_DEMO_DB_ID=chinook`).

| Profile | When |
| --- | --- |
| `AGENT_DB_PROFILE=standalone` | Chinook or Northwind (env selects which) |
| `AGENT_DB_PROFILE=tend` | Gold / eval-aligned TEND schemas |

Both Chinook and Northwind are loaded in Docker. See [status.md](status.md).

## Where code lives

Everything under `agent/` per spec §12 — see [implementation-plan.md](implementation-plan.md).

## GPT-5

Not used. See [llm-alternative.md](llm-alternative.md) for Ollama options (Qwen 2.5 7B recommended, Gemma 3 4B fallback).
