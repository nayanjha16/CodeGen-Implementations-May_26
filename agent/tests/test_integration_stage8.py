"""Stage 8 integration tests — Chinook demo on TEND Docker (skip if offline)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from agent.mcp.registry import invoke_tool
from agent.orchestration import AgentRunner
from agent.tools.execution_tool import ExecutionTool, execute_query
from agent.tools.schema_tool import SchemaTool, extract_schema, select_relevant_tables
from agent.database.postgres import PostgresExecutor


pytestmark = [pytest.mark.integration, pytest.mark.docker]


def test_chinook_postgres_has_eleven_tables(docker_stack: None) -> None:
    snapshot = PostgresExecutor().introspect_schema(db_id="chinook")
    assert snapshot.db_id == "chinook"
    assert len(snapshot.tables) == 11


def test_chinook_customer_count_postgres(docker_stack: None) -> None:
    result = execute_query(
        'SELECT COUNT(*) AS c FROM "Customer"',
        engine="postgres",
        db_id="chinook",
        allowed_tables={"Customer"},
    )
    assert result["success"] is True
    assert result["rows"][0]["c"] == 59


def test_chinook_customer_count_mongo(docker_stack: None) -> None:
    result = execute_query(
        "db.customer.countDocuments({})",
        engine="mongo",
        db_id="chinook",
    )
    assert result["success"] is True
    assert result["rows"][0]["count"] == 59


def test_schema_tool_customer_question_selects_one_table(docker_stack: None) -> None:
    with SchemaTool() as tool:
        extracted = tool.extract("How many customers are in the database?", db_id="chinook")
    assert extracted.tables == ["Customer"]
    assert "Customer" in extracted.schema_ddl


def test_mcp_extract_schema_matches_direct_call(docker_stack: None) -> None:
    question = "How many customers are in the database?"
    direct = extract_schema(question, db_id="chinook")
    via_mcp = invoke_tool("extract_schema", {"question": question, "db_id": "chinook"})
    assert via_mcp["tables"] == direct["tables"]
    assert via_mcp["db_id"] == "chinook"
    assert "Customer" in via_mcp["schema_ddl"]


def test_mcp_execute_query_matches_direct_call(docker_stack: None) -> None:
    sql = 'SELECT COUNT(*) AS c FROM "Customer"'
    args = {
        "query": sql,
        "engine": "postgres",
        "db_id": "chinook",
        "allowed_tables": ["Customer"],
    }
    direct = execute_query(**args)
    via_mcp = invoke_tool("execute_query", args)
    assert via_mcp["success"] == direct["success"]
    assert via_mcp["rows"] == direct["rows"]


def test_runner_validate_sql_live_chinook(docker_stack: None) -> None:
    runner = AgentRunner(
        detector=MagicMock(),
        llm=MagicMock(),
        schema_tool=MagicMock(),
        fastapi_tool=MagicMock(),
        execution_tool=MagicMock(),
        postgres=PostgresExecutor(),
    )
    runner.detector.detect.return_value = MagicMock(
        intent="validate_sql", confidence=1.0, source="explicit"
    )
    try:
        result = runner.run(
            "Validate SQL",
            explicit_intent="validate_sql",
            db_id="chinook",
            sql='SELECT COUNT(*) FROM "Customer"',
        )
    finally:
        runner.close()

    assert result.error is None
    assert "passed validation" in result.answer.lower()
    runner.execution_tool.run.assert_not_called()


def test_runner_text2sql_retry_recovers_with_live_postgres(docker_stack: None) -> None:
    from agent.tools.schema_tool import SchemaExtractionResult

    schema_result = SchemaExtractionResult(
        tables=["Customer"],
        columns=[{"table": "Customer", "column": "CustomerId", "type": "integer"}],
        relationships=[],
        schema_ddl='CREATE TABLE "Customer" ("CustomerId" INTEGER);',
        nosql_schema="{}",
        db_id="chinook",
        mongo_collections=["customer"],
    )

    fastapi = MagicMock()
    fastapi.generate_sql.side_effect = [
        'SELECT COUNT(*) FROM "Customer" WHERE "NotAColumn" = 1',
        'SELECT COUNT(*) AS c FROM "Customer"',
    ]

    llm = MagicMock()
    llm.summarize_results.return_value = "There are 59 customers."

    runner = AgentRunner(
        detector=MagicMock(),
        llm=llm,
        schema_tool=MagicMock(),
        fastapi_tool=fastapi,
        execution_tool=ExecutionTool(),
        postgres=PostgresExecutor(),
    )
    runner.detector.detect.return_value = MagicMock(intent="text2sql", confidence=1.0, source="rules")
    runner.schema_tool.extract.return_value = schema_result

    try:
        result = runner.run("How many customers?", db_id="chinook")
    finally:
        runner.close()

    assert result.error is None
    assert fastapi.generate_sql.call_count == 2
    count = result.rows[0].get("c", result.rows[0].get("count"))
    assert count == 59


def test_select_relevant_tables_on_live_chinook_snapshot(docker_stack: None) -> None:
    snapshot = PostgresExecutor().introspect_schema(db_id="chinook")
    selected = select_relevant_tables(snapshot, "How many customers are in the database?")
    assert selected == {"Customer"}


def test_live_snapshot_is_chinook_not_northwind(docker_stack: None) -> None:
    table_names = {table.name for table in PostgresExecutor().introspect_schema(db_id="chinook").tables}
    assert "Customer" in table_names
    assert "customers" not in table_names
