"""Stage 6 unit tests — runner and LangGraph (mocked tools/LLM)."""

from __future__ import annotations

from unittest.mock import MagicMock

from agent.orchestration import AgentRunner, build_agent_graph, run_agent_graph
from agent.tools.schema_tool import SchemaExtractionResult
from agent.database.postgres import ColumnInfo, SchemaSnapshot, TableSchema


def _schema_result() -> SchemaExtractionResult:
    return SchemaExtractionResult(
        tables=["Customer"],
        columns=[{"table": "Customer", "column": "CustomerId", "type": "integer"}],
        relationships=[],
        schema_ddl='CREATE TABLE "Customer" ("CustomerId" integer);',
        nosql_schema='{"customer": {}}',
        db_id="chinook",
        mongo_collections=["customer"],
    )


def _runner_with_mocks() -> AgentRunner:
    llm = MagicMock()
    llm.summarize_results.return_value = "There are 59 customers."

    schema_tool = MagicMock()
    schema_tool.extract.return_value = _schema_result()

    fastapi = MagicMock()
    fastapi.generate_sql.return_value = 'SELECT COUNT(*) AS c FROM "Customer"'

    execution = MagicMock()
    execution.run.return_value = MagicMock(
        success=True,
        rows=[{"c": 59}],
        error=None,
        row_count=1,
    )

    detector = MagicMock()
    detector.detect.return_value = MagicMock(intent="text2sql", confidence=0.9, source="rules")

    return AgentRunner(
        detector=detector,
        llm=llm,
        schema_tool=schema_tool,
        fastapi_tool=fastapi,
        execution_tool=execution,
        postgres=MagicMock(),
    )


def test_runner_text2sql_happy_path() -> None:
    runner = _runner_with_mocks()
    result = runner.run("How many customers are there?")
    assert "59" in result.answer
    assert "SELECT" in result.sql
    assert result.intent == "text2sql"
    assert result.error is None


def test_runner_validate_sql_no_execute() -> None:
    runner = _runner_with_mocks()
    runner.detector.detect.return_value = MagicMock(
        intent="validate_sql", confidence=1.0, source="explicit"
    )
    runner.postgres.introspect_schema.return_value = SchemaSnapshot(
        db_id="chinook",
        dataset="spider",
        schema_name="public",
        tables=[TableSchema("Customer", [ColumnInfo("CustomerId", "integer", False)])],
        foreign_keys=[],
    )
    result = runner.run(
        "Validate this SQL",
        explicit_intent="validate_sql",
        sql='SELECT COUNT(*) FROM "Customer"',
    )
    assert "passed validation" in result.answer.lower()
    runner.execution_tool.run.assert_not_called()


def test_graph_invoke_returns_answer() -> None:
    runner = _runner_with_mocks()
    graph = build_agent_graph(runner=runner)
    final = graph.invoke({"user_message": "How many customers?"})
    assert "59" in final["answer"]
    assert final["intent"] == "text2sql"


def test_run_agent_graph_wrapper() -> None:
    runner = _runner_with_mocks()
    result = run_agent_graph("How many customers?", runner=runner)
    assert result.answer
    assert result.intent == "text2sql"
