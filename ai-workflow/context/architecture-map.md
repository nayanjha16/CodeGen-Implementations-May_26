# Architecture Map (Context Sync)

> Synced from `ai-workflow/research/architecture/architecture-map.md` on 2026-07-19  
> **Active initiative:** `database-agent`

## Target flow

`User → Agent (LangGraph) → [Schema | Capstone API | Execution] tools → NL answer`

## Implemented today

- **Capstone API:** `fastapi-deploy/codegen_api` → Cloud Run  
  URL: `https://codegen-api-161349047936.asia-south2.run.app`
- **Eval / training:** `src/` pipeline (not wired to agent)

## Missing

- `agent/` Python modules, `tools/`, `mcp/`, retry loop, orchestrator LLM

## Key gap

Spec uses `/generate/*`; deployed API uses `/v1/chat/completions` — adapter required.

See full map: [research/architecture/architecture-map.md](../research/architecture/architecture-map.md)
