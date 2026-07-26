# Architecture Map (Context Sync)

> Synced from `ai-workflow/research/architecture/architecture-map.md` on 2026-07-26  
> **Active initiative:** `database-agent` — **COMPLETE**

## Target flow

`User → Agent (LangGraph) → [Schema | Capstone API | Execution] tools → NL answer`

## Implemented

- **Agent:** `agent/` — LangGraph, MCP, CLI, Web UI (88 tests)
- **Capstone API:** `fastapi-deploy/codegen_api` → Cloud Run (LoRA v3)
- **Eval / training:** `src/` pipeline (unchanged; agent imports prompts at runtime)

## Entry points

- CLI: `python -m agent.main`
- MCP: `python -m agent.mcp.server`
- Web: `python -m agent.web`

## Resolved

- API contract: **client adapter** to `/v1/chat/completions` + `intent` (see `database-agent-approval.md`)

See full map: [research/architecture/architecture-map.md](../research/architecture/architecture-map.md)
