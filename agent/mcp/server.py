"""MCP stdio server exposing the three database agent tools (Stage 7)."""

from __future__ import annotations

import json
from typing import Any

import anyio
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from agent.mcp.registry import invoke_tool, list_tool_specs

SERVER_NAME = "codegen-database-agent"


def create_server() -> Server:
    """Build the low-level MCP server wired to the tool registry."""
    server = Server(SERVER_NAME)

    @server.list_tools()
    async def _list_tools() -> list[types.Tool]:
        return list_tool_specs()

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
        try:
            result = invoke_tool(name, arguments)
            payload = json.dumps(result, default=str)
        except Exception as exc:  # noqa: BLE001 — surface tool errors to MCP client
            payload = json.dumps({"error": str(exc)})
        return [types.TextContent(type="text", text=payload)]

    return server


async def run_stdio_server() -> None:
    server = create_server()
    init_options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, init_options)


def main() -> None:
    """Entry point: python -m agent.mcp.server"""
    anyio.run(run_stdio_server)


if __name__ == "__main__":
    main()
