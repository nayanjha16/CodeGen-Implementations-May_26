# Open Questions — AI Database Agent

> **Status:** **RESOLVED** (2026-07-26)  
> **Decisions:** [database-agent-approval.md](../../planning/approvals/database-agent-approval.md)

All research questions were decided at approval time and implemented through Stage 10.

| Topic | Decision |
|-------|----------|
| API contract | Client adapter to `/v1/chat/completions` + explicit `intent` |
| Package layout | Extend `agent/` (not separate `database-agent/` folder) |
| Tool order | LangGraph native tools first, MCP wrapper second |
| Orchestrator LLM | Ollama `gemma3:4b` (local); CodeGen on Cloud Run for SQL |
| Schema tool | Keyword matching on introspected metadata (no embeddings) |
| Demo DB | Standalone Chinook/Northwind via TEND Docker |
| MVP scope | text2sql, sql2nosql, nosql2doc, explain, validate |

**Demo client:** `agent/web/` — LangGraph agent with Web UI, MCP, and CLI.
