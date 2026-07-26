# Executive Summary — AI Database Agent (`database-agent`)

> **Research date:** 2026-07-19  
> **Feature slug:** `database-agent`  
> **Primary spec:** `agent/doc/agent.md` (v1.0, IIIT Hyderabad AIML Capstone)  
> **Research phase:** Complete — ready for Planning

## Project Purpose

Build an **AI Database Agent** that answers natural-language database questions by **orchestrating tools** (schema retrieval, fine-tuned model inference, query execution, retry on failure) instead of generating SQL directly in the orchestrator LLM.

The capstone demonstrates **Agentic AI**: MCP tool calling, LangGraph-style planning, fine-tuned CodeGen LoRA adapters, live database execution, self-correction (max 3 retries), and natural-language summarization of results.

This sits on top of an existing **CodeGen Studio** research repo that already provides:

- Three-task pipeline models: **text2sql**, **sql2nosql**, **nosql2doc**
- LoRA training and evaluation (`src/training/`, `scripts/run_baseline_eval.py`)
- **Deployed inference API** (`fastapi-deploy/codegen_api`) on Google Cloud Run
- TEND-backed execution comparison for eval (`src/evaluation/database_execution.py`)

The **agent layer is greenfield** — only the specification exists under `agent/doc/agent.md`.

## Business / Capstone Goals

| Goal | How the agent demonstrates it |
|------|-------------------------------|
| Agentic orchestration | LLM agent selects tools; never writes SQL directly |
| MCP architecture | Three MCP-compatible tools exposed via MCP server |
| Fine-tuned models | Capstone FastAPI tool calls Cloud Run LoRA v2 adapters |
| Database interaction | Execution tool runs Postgres (and later Mongo) queries |
| Error recovery | Failed execution → error fed back to model → retry (≤3) |
| Production readiness | Modular tools, config-driven URLs, deployable services |

## Architecture Overview (Target)

```
User
  → AI Agent (LangGraph + orchestrator LLM)
       → Schema Tool        (relevant tables/columns only)
       → Capstone API Tool  (HTTP → codegen-api Cloud Run)
       → Execution Tool     (Postgres / Mongo → rows)
       → Retry loop on execution failure
  → Natural language answer
```

**Current state:** Only the **Capstone API** (middle box) is implemented and deployed. Agent, MCP server, schema tool, execution tool wrapper, and retry loop are **not implemented**.

## Technology Stack (Target vs Actual)

| Component | Spec (`agent.md`) | Actual today |
|-----------|-------------------|--------------|
| Agent framework | LangGraph or OpenAI Agents SDK | **None** |
| Orchestrator LLM | GPT-class with tool calling | **None** (classifier is rules/embeddings inside FastAPI, not an agent) |
| Tool protocol | MCP | **None** |
| Capstone API | FastAPI `/generate/*` | **`codegen_api`** — OpenAI `/v1/chat/completions` on Cloud Run |
| Fine-tuned models | Text2SQL, SQL2NoSQL, SQL2Doc LoRA | **v2 on Hub** (`codegenstudio`), served from Cloud Run |
| Databases | PostgreSQL, MongoDB | **TEND** Postgres/Mongo for eval only; no agent-facing execution API |
| Deployment | Docker / Cloud | **Cloud Run** live at `https://codegen-api-161349047936.asia-south2.run.app` |

## Key Workflows

### Existing (implemented)

1. **Training** — `train_lora.py` / `train_all_lora.py` → `models/checkpoints/v{1,2,3}/`
2. **Evaluation** — `run_baseline_eval.py` → metrics + CSVs under `results/`
3. **Inference API** — User message (+ schema in prompt) → classifier → LoRA adapter → generated SQL/NoSQL/doc
4. **Execution eval** — Compare predicted vs gold query results via TEND (`database_execution.py`)

### Target (agent — not implemented)

1. User question → agent detects intent (text2sql / sql2nosql / doc / explain)
2. Schema tool returns subset of relevant schema
3. FastAPI tool calls Cloud Run with schema-enriched prompt (force intent to avoid `clarify`)
4. Execution tool runs query; on error, agent retries with error context (≤3)
5. Agent summarizes rows in natural language

## Related Prior Work in Repo

| Initiative | Status | Relevance to agent |
|------------|--------|-------------------|
| LoRA fine-tuning | Implemented (v1 smoke, v2 full) | Models served by Cloud Run |
| `fastapi-deploy` | Deployed | **Capstone FastAPI tool** target |
| `text2sql-ui-tool` | Documented in `ai-workflow/`; **`tool/` absent on disk** | Planned schema loader, FastAPI client, pipeline — can inform agent tools |
| `hf-deploy` | Removed | Replaced by `fastapi-deploy` |

## Research Conclusion

Implementation should **reuse** `codegen_api` (HTTP client), `database_execution.py` patterns (execution), and prompt builders in `src/text2sql/` — not duplicate model logic in the agent.

Planning must resolve: API contract shim (`/generate/*` vs `/v1/chat/completions`), orchestrator LLM choice, schema tool v1 strategy, and MCP vs LangGraph-native tools first.

**Next phase:** Planning (`ai-workflow/planning/feature-plans/database-agent-plan.md`).
