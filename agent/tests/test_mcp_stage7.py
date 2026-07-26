"""Stage 7 unit tests — MCP registry and tool dispatch."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agent.mcp.registry import invoke_tool, list_tool_specs


def test_list_tool_specs_registers_three_tools() -> None:
    specs = list_tool_specs()
    names = {tool.name for tool in specs}
    assert names == {"extract_schema", "codegen_generate", "execute_query"}


def test_invoke_unknown_tool_raises() -> None:
    with pytest.raises(KeyError, match="Unknown MCP tool"):
        invoke_tool("missing_tool", {})


def test_invoke_extract_schema_delegates() -> None:
    payload = {
        "tables": ["Customer"],
        "columns": [],
        "relationships": [],
        "schema_ddl": 'CREATE TABLE "Customer" ("CustomerId" integer);',
        "nosql_schema": "{}",
        "db_id": "chinook",
        "mongo_collections": ["customer"],
    }
    with patch("agent.mcp.registry.extract_schema", return_value=payload) as mock_extract:
        result = invoke_tool(
            "extract_schema",
            {"question": "How many customers?", "db_id": "chinook"},
        )
    mock_extract.assert_called_once_with("How many customers?", db_id="chinook", dataset=None)
    assert result["db_id"] == "chinook"


def test_invoke_codegen_generate_sql() -> None:
    mock_tool = MagicMock()
    mock_tool.generate_sql.return_value = 'SELECT COUNT(*) FROM "Customer"'
    with patch("agent.mcp.registry.FastApiTool", return_value=mock_tool):
        result = invoke_tool(
            "codegen_generate",
            {
                "operation": "sql",
                "question": "count customers",
                "schema": 'CREATE TABLE "Customer" ("CustomerId" integer);',
            },
        )
    assert result["sql"].startswith("SELECT")
    mock_tool.generate_sql.assert_called_once()


def test_invoke_codegen_generate_nosql() -> None:
    mock_tool = MagicMock()
    mock_tool.generate_nosql.return_value = "db.customer.find({})"
    with patch("agent.mcp.registry.FastApiTool", return_value=mock_tool):
        result = invoke_tool(
            "codegen_generate",
            {
                "operation": "nosql",
                "sql_query": 'SELECT * FROM "Customer"',
                "schema": "CREATE TABLE customer (id INT);",
            },
        )
    assert "find" in result["mongo_query"]


def test_invoke_execute_query_delegates() -> None:
    payload = {"rows": [{"c": 59}], "success": True, "error": None, "row_count": 1, "engine": "postgres"}
    with patch("agent.mcp.registry.execute_query", return_value=payload) as mock_exec:
        result = invoke_tool(
            "execute_query",
            {
                "query": 'SELECT COUNT(*) AS c FROM "Customer"',
                "engine": "postgres",
                "allowed_tables": ["Customer"],
            },
        )
    mock_exec.assert_called_once()
    assert result["success"] is True


def test_create_server_builds() -> None:
    from agent.mcp.server import SERVER_NAME, create_server

    server = create_server()
    assert server.name == SERVER_NAME
