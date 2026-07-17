"""Integration tests for Text2SqlPipeline (mocked dependencies)."""

from unittest.mock import MagicMock, patch

import pandas as pd

from tool.core.activity_logger import ActivityLogger
from tool.core.schema_loader import TableSchema
from tool.core.schema_selector import SchemaSelectionResult
from tool.core.settings_store import AppSettings, DatabaseConnection
from tool.pipeline.text2sql_pipeline import Text2SqlPipeline


def _settings() -> AppSettings:
    conn = DatabaseConnection(
        id="c1",
        name="Test",
        host="localhost",
        port=5432,
        database="db",
        username="u",
        password="p",
    )
    return AppSettings(connections=[conn], active_connection_id=conn.id)


def test_pipeline_success():
    settings = _settings()
    logger = ActivityLogger()
    pipeline = Text2SqlPipeline(settings=settings)

    mock_engine = MagicMock()
    tables = [TableSchema(name="users", ddl="CREATE TABLE users (id INT);", columns=["id"])]
    selection = SchemaSelectionResult(selected=tables, scores={"users": 0.9}, method="embedding", fk_expanded=[])

    with (
        patch("tool.pipeline.text2sql_pipeline.get_active_engine", return_value=(mock_engine, settings.connections[0])),
        patch("tool.pipeline.text2sql_pipeline.load_all_tables", return_value=tables),
        patch("tool.pipeline.text2sql_pipeline.select_tables_for_prompt", return_value=selection),
        patch("tool.pipeline.text2sql_pipeline.FastApiInferenceClient") as mock_client_cls,
        patch("tool.pipeline.text2sql_pipeline.execute_readonly_sql") as mock_exec,
    ):
        mock_client_cls.return_value.generate_sql.return_value = "SELECT id FROM users"
        mock_exec.return_value = MagicMock(
            dataframe=pd.DataFrame({"id": [1]}),
            row_count=1,
            duration_ms=5.0,
            truncated=False,
            sql="SELECT id FROM users",
        )
        result = pipeline.run("show all users", logger=logger)

    assert result.success is True
    assert result.generated_sql == "SELECT id FROM users"
    assert result.result_df is not None
    events = {e.event for e in logger.events}
    assert "connection_established" in events
    assert "tables_selected" in events or "schema_loaded" in events
    assert "prompt_built" in events
    assert "validation_passed" in events

    prompt_event = next(e for e in logger.events if e.event == "prompt_built")
    assert "tables" in prompt_event.details
    prompt_body = next((e for e in logger.events if e.event == "prompt_body"), None)
    assert prompt_body is not None
    assert "show all users" in prompt_body.details.get("prompt", "")


def test_pipeline_execution_error_preserves_sql():
    settings = _settings()
    logger = ActivityLogger()
    mock_engine = MagicMock()
    tables = [TableSchema(name="users", ddl="CREATE TABLE users (id INT);", columns=["id"])]
    selection = SchemaSelectionResult(selected=tables, scores={"users": 0.9}, method="full_schema", fk_expanded=[])

    with (
        patch("tool.pipeline.text2sql_pipeline.get_active_engine", return_value=(mock_engine, settings.connections[0])),
        patch("tool.pipeline.text2sql_pipeline.load_all_tables", return_value=tables),
        patch("tool.pipeline.text2sql_pipeline.select_tables_for_prompt", return_value=selection),
        patch("tool.pipeline.text2sql_pipeline.FastApiInferenceClient") as mock_client_cls,
        patch("tool.pipeline.text2sql_pipeline.execute_readonly_sql", side_effect=RuntimeError("db timeout")),
    ):
        mock_client_cls.return_value.generate_sql.return_value = "SELECT id FROM users"
        result = Text2SqlPipeline(settings=settings).run("show users", logger=logger)

    assert result.success is False
    assert result.generated_sql == "SELECT id FROM users"
    assert "db timeout" in (result.error or "")


def test_pipeline_empty_question():
    result = Text2SqlPipeline(settings=_settings()).run("  ", logger=ActivityLogger())
    assert result.success is False


def test_pipeline_validation_failure():
    settings = _settings()
    logger = ActivityLogger()
    mock_engine = MagicMock()
    tables = [TableSchema(name="users", ddl="CREATE TABLE users (id INT);", columns=["id"])]
    selection = SchemaSelectionResult(selected=tables, scores={"users": 0.9}, method="full_schema", fk_expanded=[])

    with (
        patch("tool.pipeline.text2sql_pipeline.get_active_engine", return_value=(mock_engine, settings.connections[0])),
        patch("tool.pipeline.text2sql_pipeline.load_all_tables", return_value=tables),
        patch("tool.pipeline.text2sql_pipeline.select_tables_for_prompt", return_value=selection),
        patch("tool.pipeline.text2sql_pipeline.FastApiInferenceClient") as mock_client_cls,
    ):
        mock_client_cls.return_value.generate_sql.return_value = "DELETE FROM users"
        result = Text2SqlPipeline(settings=settings).run("remove users", logger=logger)

    assert result.success is False
    assert result.validation_status is not None
    assert result.validation_status["passed"] is False
