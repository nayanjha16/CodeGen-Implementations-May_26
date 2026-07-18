"""Tests for sql2nosql pipeline."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from tool.core.activity_logger import ActivityLogger
from tool.core.schema_loader import TableSchema
from tool.pipeline.sql2nosql_pipeline import Sql2NoSqlPipeline


@pytest.fixture
def pipeline(app_settings) -> Sql2NoSqlPipeline:
    return Sql2NoSqlPipeline(settings=app_settings)


def test_execute_rejects_empty_sql(pipeline: Sql2NoSqlPipeline):
    logger = ActivityLogger()
    result = pipeline.execute("   ", logger=logger)
    assert result.success is False
    assert "SQL query" in (result.error or "")


def test_execute_rejects_unsafe_sql(pipeline: Sql2NoSqlPipeline):
    logger = ActivityLogger()
    result = pipeline.execute("DELETE FROM film", logger=logger)
    assert result.success is False
    assert result.validation_status is not None


@patch("tool.pipeline.sql2nosql_pipeline.get_active_mongo_client")
@patch("tool.pipeline.sql2nosql_pipeline.get_active_engine")
@patch("tool.pipeline.sql2nosql_pipeline.load_all_tables")
def test_execute_success(
    mock_load_tables,
    mock_engine,
    mock_mongo_client,
    pipeline: Sql2NoSqlPipeline,
    app_settings,
):
    mock_engine.return_value = (MagicMock(), app_settings.connections[0])
    mock_mongo = MagicMock()
    mock_mongo.admin.command.return_value = {"ok": 1}
    mock_mongo_client.return_value = (mock_mongo, app_settings.mongo_connections[0])

    table = TableSchema(
        name="film",
        ddl="CREATE TABLE film (film_id INTEGER, title TEXT);",
        columns=["film_id", "title"],
    )
    mock_load_tables.return_value = [table]

    with patch("tool.pipeline.sql2nosql_pipeline.FastApiInferenceClient") as mock_client_cls:
        mock_client = mock_client_cls.return_value
        mock_client.generate_nosql.return_value = "db.film.countDocuments({})"
        mock_client.generate_documentation.return_value = "Counts all films in the catalog."

        with patch("tool.pipeline.sql2nosql_pipeline.execute_mongo_query") as mock_exec:
            mock_exec.return_value = MagicMock(
                error=None,
                dataframe=pd.DataFrame([{"count": 1000}]),
                row_count=1,
                duration_ms=12.3,
                truncated=False,
            )

            logger = ActivityLogger()
            result = pipeline.execute("SELECT COUNT(*) FROM film", logger=logger)

    assert result.success is True
    assert result.generated_nosql == "db.film.countDocuments({})"
    assert result.documentation == "Counts all films in the catalog."
    assert result.selected_tables == ["film"]

    events = {e.event for e in logger.events}
    assert "sql_tables_parsed" in events
    assert "tables_selected" in events
    assert "doc_prompt_body" in events
    assert "documentation_start" in events
    assert "documentation_ready" in events

    parsed_event = next(e for e in logger.events if e.event == "sql_tables_parsed")
    assert parsed_event.details["parsed"] == ["film"]

    selected_event = next(e for e in logger.events if e.event == "tables_selected")
    assert selected_event.details["method"] == "sql_parse"
    assert selected_event.details["selected"] == ["film"]
