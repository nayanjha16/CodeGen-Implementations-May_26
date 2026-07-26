# Stage 7 — MCP Server

**Date:** 2026-07-26  
**Status:** Complete

## Implemented

- `agent/mcp/registry.py` — tool specs + `invoke_tool()` dispatch to existing Stage 3 tools
- `agent/mcp/server.py` — stdio MCP server (`python -m agent.mcp.server`)
- `agent/tests/test_mcp_stage7.py` — registry unit tests (7 cases)
- `agent/requirements.txt` — added `mcp>=1.0`
- Docs: `agent/README.md`, `ai-workflow/planning/feature-plans/agent/status.md`

## MCP tools (spec §7)

| Name | Delegates to |
| --- | --- |
| `extract_schema` | `schema_tool.extract_schema` |
| `codegen_generate` | `fastapi_tool` (operations: sql, nosql, documentation) |
| `execute_query` | `execution_tool.execute_query` |

## Default demo

Chinook via single `agent/.env` (`AGENT_DEMO_DB_ID=chinook`).

## Blockers

None.

## Assumptions

- stdio transport is sufficient for Cursor/local MCP clients (no HTTP SSE in initial build)
- LangGraph runner continues calling tools directly; MCP shares registry handlers
