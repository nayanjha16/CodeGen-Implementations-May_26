"""MCP tool registry — shared by LangGraph runner and MCP server (agent.md §7)."""

from __future__ import annotations

from typing import Any, Callable

import mcp.types as types

from agent.lib.sql_validation import normalize_generated_sql
from agent.tools.execution_tool import execute_query
from agent.tools.fastapi_tool import FastApiTool
from agent.tools.schema_tool import extract_schema

ToolHandler = Callable[[dict[str, Any]], Any]

_CODEGEN_OPERATIONS = frozenset({"sql", "nosql", "documentation"})
_EXECUTION_ENGINES = frozenset({"auto", "postgres", "mongo"})


def _require_str(arguments: dict[str, Any], key: str) -> str:
    value = arguments.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} is required")
    return value.strip()


def _handle_extract_schema(arguments: dict[str, Any]) -> dict[str, Any]:
    question = _require_str(arguments, "question")
    db_id = arguments.get("db_id")
    dataset = arguments.get("dataset")
    return extract_schema(
        question,
        db_id=str(db_id).strip() if db_id else None,
        dataset=str(dataset).strip() if dataset else None,
    )


def _handle_codegen_generate(arguments: dict[str, Any]) -> dict[str, Any]:
    operation = _require_str(arguments, "operation").lower()
    if operation not in _CODEGEN_OPERATIONS:
        raise ValueError(f"operation must be one of: {', '.join(sorted(_CODEGEN_OPERATIONS))}")

    tool = FastApiTool()
    schema = str(arguments.get("schema") or "")

    if operation == "sql":
        question = _require_str(arguments, "question")
        sql = tool.generate_sql(
            question,
            schema,
            previous_sql=arguments.get("previous_sql"),
            db_error=arguments.get("db_error"),
        )
        if schema:
            sql = normalize_generated_sql(sql, schema)
        return {"operation": operation, "sql": sql}

    if operation == "nosql":
        sql_query = _require_str(arguments, "sql_query")
        mongo_query = tool.generate_nosql(
            sql_query,
            schema,
            nosql_schema=arguments.get("nosql_schema"),
        )
        return {"operation": operation, "mongo_query": mongo_query}

    mongodb_query = _require_str(arguments, "mongodb_query")
    documentation = tool.generate_documentation(
        mongodb_query,
        schema=schema,
        nosql_schema=arguments.get("nosql_schema"),
        question=str(arguments.get("question") or ""),
    )
    return {"operation": operation, "documentation": documentation}


def _handle_execute_query(arguments: dict[str, Any]) -> dict[str, Any]:
    query = _require_str(arguments, "query")
    engine = str(arguments.get("engine") or "auto").lower()
    if engine not in _EXECUTION_ENGINES:
        raise ValueError(f"engine must be one of: {', '.join(sorted(_EXECUTION_ENGINES))}")

    db_id = arguments.get("db_id")
    dataset = arguments.get("dataset")
    allowed_raw = arguments.get("allowed_tables")
    allowed_tables = None
    if allowed_raw is not None:
        if not isinstance(allowed_raw, list):
            raise ValueError("allowed_tables must be a list of table names")
        allowed_tables = {str(name) for name in allowed_raw}

    if engine == "postgres" and allowed_tables is None:
        schema_ddl = arguments.get("schema_ddl")
        if isinstance(schema_ddl, str) and schema_ddl.strip():
            query = normalize_generated_sql(query, schema_ddl)

    return execute_query(
        query,
        engine=engine,  # type: ignore[arg-type]
        db_id=str(db_id).strip() if db_id else None,
        dataset=str(dataset).strip() if dataset else None,
        allowed_tables=allowed_tables,
    )


TOOL_HANDLERS: dict[str, ToolHandler] = {
    "extract_schema": _handle_extract_schema,
    "codegen_generate": _handle_codegen_generate,
    "execute_query": _handle_execute_query,
}


def list_tool_specs() -> list[types.Tool]:
    """MCP tool definitions for list_tools."""
    return [
        types.Tool(
            name="extract_schema",
            description=(
                "Return relevant Postgres/Mongo schema slices for a natural-language question."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Natural language question about the data.",
                    },
                    "db_id": {
                        "type": "string",
                        "description": "Optional demo or TEND db_id override.",
                    },
                    "dataset": {
                        "type": "string",
                        "description": "Optional TEND dataset catalog (default from env).",
                    },
                },
                "required": ["question"],
            },
        ),
        types.Tool(
            name="codegen_generate",
            description=(
                "Generate SQL, MongoDB shell, or documentation via CodeGen API (LoRA on Cloud Run)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["sql", "nosql", "documentation"],
                        "description": "Generation task to run.",
                    },
                    "question": {
                        "type": "string",
                        "description": "NL question for sql or documentation context.",
                    },
                    "schema": {
                        "type": "string",
                        "description": "CREATE TABLE DDL for CodeGen prompts.",
                    },
                    "sql_query": {
                        "type": "string",
                        "description": "SQL input for nosql operation.",
                    },
                    "mongodb_query": {
                        "type": "string",
                        "description": "Mongo shell query for documentation operation.",
                    },
                    "nosql_schema": {
                        "type": "string",
                        "description": "Optional Mongo schema JSON for sql2nosql.",
                    },
                    "previous_sql": {
                        "type": "string",
                        "description": "Previous SQL for retry correction.",
                    },
                    "db_error": {
                        "type": "string",
                        "description": "Database error message for retry correction.",
                    },
                },
                "required": ["operation"],
            },
        ),
        types.Tool(
            name="execute_query",
            description="Execute a read-only Postgres SELECT or Mongo shell query.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL or Mongo shell query to execute.",
                    },
                    "engine": {
                        "type": "string",
                        "enum": ["auto", "postgres", "mongo"],
                        "default": "auto",
                    },
                    "db_id": {
                        "type": "string",
                        "description": "Optional demo or TEND db_id override.",
                    },
                    "dataset": {
                        "type": "string",
                        "description": "Optional TEND dataset catalog.",
                    },
                    "allowed_tables": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Postgres tables permitted in the query.",
                    },
                    "schema_ddl": {
                        "type": "string",
                        "description": "Optional DDL used to quote PascalCase identifiers.",
                    },
                },
                "required": ["query"],
            },
        ),
    ]


def invoke_tool(name: str, arguments: dict[str, Any] | None = None) -> Any:
    """Dispatch an MCP tool call to the underlying agent tool implementation."""
    handler = TOOL_HANDLERS.get(name)
    if handler is None:
        raise KeyError(f"Unknown MCP tool: {name}")
    return handler(dict(arguments or {}))
