# Project Summary (Context Sync)

> Synced from `ai-workflow/research/summaries/project-summary.md` on 2026-07-19  
> **Active initiative:** `database-agent`

## Purpose

AI Database Agent (capstone) orchestrating MCP tools — schema retrieval, Cloud Run CodeGen API, DB execution, retry — without generating SQL in the orchestrator.

## Stack

- **Deployed:** `fastapi-deploy/codegen_api` on Cloud Run (LoRA v2, `/v1/chat/completions`)
- **To build:** LangGraph agent, MCP server, three tools under `tools/`
- **Reuse:** `src/text2sql/`, `src/evaluation/database_execution.py` patterns

## Status

- Research: **complete** (2026-07-19)
- Planning: **next**
- Implementation: **not started**

See full summary: [research/summaries/project-summary.md](../research/summaries/project-summary.md)
