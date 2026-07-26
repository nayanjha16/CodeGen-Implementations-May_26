# Project Summary (Context Sync)

> Synced from `ai-workflow/research/summaries/project-summary.md` on 2026-07-26  
> **Active initiative:** `database-agent` — **COMPLETE**

## Purpose

AI Database Agent (capstone) orchestrating MCP tools — schema retrieval, Cloud Run CodeGen API, DB execution, retry — without generating SQL in the orchestrator.

## Stack

- **Deployed:** `fastapi-deploy/codegen_api` on Cloud Run (LoRA v3, `/v1/chat/completions`)
- **Built:** LangGraph agent, MCP server, three tools, Web UI — all under `agent/`
- **Reuse:** `src` prompt builders + sql_validator imported at runtime

## Status

- Research: **complete** (2026-07-19)
- Planning: **complete** (2026-07-26)
- Implementation: **complete** — Stages 1–10 (2026-07-26)
- Validation: **88 tests passed**

## Entry points

- CLI: `python -m agent.main`
- MCP: `python -m agent.mcp.server`
- Web: `python -m agent.web` → http://127.0.0.1:8080

See full summary: [research/summaries/project-summary.md](../research/summaries/project-summary.md)
