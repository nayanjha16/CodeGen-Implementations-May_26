# Executive Summary — AI Database Agent (`database-agent`)

> **Research date:** 2026-07-19 · **Implementation complete:** 2026-07-26  
> **Feature slug:** `database-agent`  
> **Primary spec:** `agent/doc/agent.md` (v1.0, IIIT Hyderabad AIML Capstone)  
> **Research phase:** Complete · **Planning:** Complete · **Implementation:** Complete (Stages 1–10)

## Project Purpose

Build an **AI Database Agent** that answers natural-language database questions by **orchestrating tools** (schema retrieval, fine-tuned model inference, query execution, retry on failure) instead of generating SQL directly in the orchestrator LLM.

The capstone demonstrates **Agentic AI**: MCP tool calling, LangGraph-style planning, fine-tuned CodeGen LoRA adapters, live database execution, self-correction (max 3 retries), and natural-language summarization of results.

This sits on top of an existing **CodeGen Studio** research repo that already provides:

- Three-task pipeline models: **text2sql**, **sql2nosql**, **nosql2doc**
- LoRA training and evaluation (`src/training/`, `scripts/run_baseline_eval.py`)
- **Deployed inference API** (`fastapi-deploy/codegen_api`) on Google Cloud Run
- TEND-backed execution comparison for eval (`src/evaluation/database_execution.py`)

The **agent layer is implemented** under `agent/` — LangGraph orchestrator, MCP server, three tools, CLI, and Web UI. See `ai-workflow/context/current-state.md`.

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

**Current state (2026-07-26):** Full agent path implemented — user question → schema tool → CodeGen API → execution → retry → NL response. Entry points: CLI (`agent.main`), MCP (`agent.mcp.server`), Web UI (`agent.web`). **88 tests passed.**

## Technology Stack (Target vs Actual)

| Component | Spec (`agent.md`) | Actual today |
|-----------|-------------------|--------------|
| Agent framework | LangGraph or OpenAI Agents SDK | **LangGraph** (`agent/orchestration/`) |
| Orchestrator LLM | GPT-class with tool calling | **Ollama** (`gemma3:4b`) |
| Tool protocol | MCP | **MCP stdio** (`agent/mcp/`) |
| Capstone API | FastAPI `/generate/*` | **`codegen_api`** — OpenAI `/v1/chat/completions` on Cloud Run |
| Fine-tuned models | Text2SQL, SQL2NoSQL, SQL2Doc LoRA | **v3 on Cloud Run** |
| Databases | PostgreSQL, MongoDB | **TEND Docker** + standalone Chinook/Northwind |
| Deployment | Docker / Cloud | **Cloud Run** + local Web UI (`agent/web/`) |

## Key Workflows

### Existing (implemented)

1. **Training** — `train_lora.py` / `train_all_lora.py` → `models/checkpoints/v{1,2,3}/`
2. **Evaluation** — `run_baseline_eval.py` → metrics + CSVs under `results/`
3. **Inference API** — User message (+ schema in prompt) → classifier → LoRA adapter → generated SQL/NoSQL/doc
4. **Execution eval** — Compare predicted vs gold query results via TEND (`database_execution.py`)

### Agent (implemented — `agent/`)

1. User question → Ollama detects intent (text2sql / sql2nosql / doc / explain / validate)
2. Schema tool returns subset of relevant schema
3. CodeGen client calls Cloud Run with schema-enriched prompt + explicit `intent`
4. Execution tool runs query; on error, retry with error context (≤3)
5. Ollama summarizes rows (or deterministic listing summary for tabular results)
6. Web UI: `python -m agent.web` for capstone demo

## Related Prior Work in Repo

| Initiative | Status | Relevance to agent |
|------------|--------|-------------------|
| LoRA fine-tuning | Implemented (v1 smoke, v2 full) | Models served by Cloud Run |
| `fastapi-deploy` | Deployed | **Capstone FastAPI tool** target |
| `text2sql-ui-tool` | Documented in `ai-workflow/`; **`tool/` absent on disk** | Planned schema loader, FastAPI client, pipeline — can inform agent tools |
| `hf-deploy` | Removed | Replaced by `fastapi-deploy` |

## Research Conclusion

Implementation should **reuse** `codegen_api` (HTTP client), `database_execution.py` patterns (execution), and prompt builders in `src/text2sql/` — not duplicate model logic in the agent.

Planning resolved all open questions — see `planning/approvals/database-agent-approval.md`. Implementation complete through Stage 10.

**Artifacts:** `planning/task-breakdowns/database-agent-tasks.md`, `planning/implementation-roadmaps/database-agent-roadmap.md`, `planning/dependency-analysis/database-agent-dependencies.md`, `validation/validation-reports/database-agent-validation.md`.
