"""Stage 3–4 unit tests — tools and validation (no live Docker/API)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agent.database.postgres import ColumnInfo, ForeignKeyInfo, SchemaSnapshot, TableSchema
from agent.lib.sql_validation import (
    normalize_generated_sql,
    referenced_tables,
    validate_sql_for_execution,
)
from agent.tools.execution_tool import ExecutionTool, detect_engine
from agent.tools.fastapi_tool import FastApiTool
from agent.tools.schema_tool import SchemaTool, select_relevant_tables


def _chinook_snapshot() -> SchemaSnapshot:
    return SchemaSnapshot(
        db_id="chinook",
        dataset="spider",
        schema_name="public",
        tables=[
            TableSchema(
                "Customer",
                [
                    ColumnInfo("CustomerId", "integer", False),
                    ColumnInfo("FirstName", "character varying", True),
                ],
            ),
            TableSchema(
                "Invoice",
                [
                    ColumnInfo("InvoiceId", "integer", False),
                    ColumnInfo("CustomerId", "integer", False),
                ],
            ),
            TableSchema("Album", [ColumnInfo("AlbumId", "integer", False)]),
        ],
        foreign_keys=[
            ForeignKeyInfo("Invoice", "CustomerId", "Customer", "CustomerId"),
        ],
    )


def test_select_relevant_tables_matches_customer_and_fk() -> None:
    selected = select_relevant_tables(_chinook_snapshot(), "How many customers do we have?")
    assert selected == {"Customer"}


def test_select_relevant_tables_ignores_stopword_in() -> None:
    selected = select_relevant_tables(_chinook_snapshot(), "How many customers are in the database?")
    assert "Customer" in selected
    assert "Album" not in selected
    assert "Invoice" not in selected


def test_select_relevant_tables_expands_foreign_keys() -> None:
    selected = select_relevant_tables(_chinook_snapshot(), "Show invoice totals by customer")
    assert "Invoice" in selected
    assert "Customer" in selected


def test_select_relevant_tables_includes_multi_table_entities() -> None:
    snapshot = SchemaSnapshot(
        db_id="chinook",
        dataset="spider",
        schema_name="public",
        tables=[
            TableSchema(
                "Track",
                [
                    ColumnInfo("TrackId", "integer", False),
                    ColumnInfo("Name", "character varying", True),
                    ColumnInfo("UnitPrice", "numeric", True),
                    ColumnInfo("AlbumId", "integer", False),
                ],
            ),
            TableSchema(
                "Album",
                [
                    ColumnInfo("AlbumId", "integer", False),
                    ColumnInfo("Title", "character varying", True),
                    ColumnInfo("ArtistId", "integer", False),
                ],
            ),
            TableSchema(
                "Artist",
                [
                    ColumnInfo("ArtistId", "integer", False),
                    ColumnInfo("Name", "character varying", True),
                ],
            ),
        ],
        foreign_keys=[
            ForeignKeyInfo("Track", "AlbumId", "Album", "AlbumId"),
            ForeignKeyInfo("Album", "ArtistId", "Artist", "ArtistId"),
        ],
    )
    selected = select_relevant_tables(
        snapshot,
        "List the top 5 tracks by unit price with album title and artist name.",
    )
    assert selected == {"Track", "Album", "Artist"}


def test_select_relevant_tables_fallback_all_when_no_match() -> None:
    selected = select_relevant_tables(_chinook_snapshot(), "xyz unknown token only")
    assert selected == {"Customer", "Invoice", "Album"}


def test_schema_tool_extract_builds_ddl_and_relationships() -> None:
    snapshot = _chinook_snapshot()
    postgres = MagicMock()
    postgres.introspect_schema.return_value = snapshot
    mongo = MagicMock()
    mongo.list_collections.return_value = ["customer", "invoice", "album"]

    tool = SchemaTool(postgres=postgres, mongo=mongo)
    result = tool.extract("customer invoices", db_id="chinook")

    assert "Customer" in result.tables
    assert "CREATE TABLE" in result.schema_ddl
    assert any(rel["from_table"] == "Invoice" for rel in result.relationships)
    assert "customer" in result.mongo_collections


def test_detect_engine() -> None:
    assert detect_engine("db.customer.find({})") == "mongo"
    assert detect_engine("SELECT 1") == "postgres"


def test_execution_tool_routes_sql_through_postgres() -> None:
    postgres = MagicMock()
    postgres.execute.return_value = MagicMock(
        rows=[{"count": 1}],
        row_count=1,
        truncated=False,
        error=None,
        ok=True,
    )
    mongo = MagicMock()
    tool = ExecutionTool(postgres=postgres, mongo=mongo)
    result = tool.run('SELECT COUNT(*) FROM "Customer"', allowed_tables={"Customer"})

    assert result.success is True
    assert result.engine == "postgres"
    postgres.execute.assert_called_once()


def test_execution_tool_rejects_unknown_table() -> None:
    tool = ExecutionTool(postgres=MagicMock(), mongo=MagicMock())
    result = tool.run(
        'SELECT * FROM "Other"',
        allowed_tables={"Customer"},
    )
    assert result.success is False
    assert "unknown tables" in (result.error or "").lower()


def test_fastapi_tool_delegates_to_client() -> None:
    client = MagicMock()
    client.generate_sql.return_value = "SELECT 1"
    tool = FastApiTool(client=client)
    sql = tool.generate_sql("q", "schema")
    assert sql == "SELECT 1"
    client.generate_sql.assert_called_once_with("q", "schema", previous_sql=None, db_error=None)


def test_fastapi_tool_explanation_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        FastApiTool(client=MagicMock()).generate_explanation("SELECT 1")


def test_quote_known_identifiers_fixes_chinook_tables() -> None:
    ddl = 'CREATE TABLE "Customer" ("CustomerId" INTEGER);'
    sql = 'SELECT count(*) FROM Customer WHERE CustomerId IN (SELECT CustomerId FROM "Customer")'
    fixed = normalize_generated_sql(sql, ddl)
    assert 'FROM "Customer"' in fixed
    assert '"CustomerId"' in fixed


def test_validate_sql_for_execution_rejects_delete() -> None:
    assert validate_sql_for_execution("DELETE FROM customer") is not None


def test_referenced_tables_parses_quoted_identifiers() -> None:
    tables = referenced_tables('SELECT * FROM "Customer" JOIN "Invoice" ON 1=1')
    assert tables == {"Customer", "Invoice"}


def test_generate_sql_via_fastapi_tool_mock_http() -> None:
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "SELECT COUNT(*) FROM customer"}}]
    }
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.post.return_value = mock_response

    with patch("agent.clients.codegen_client.httpx.Client", return_value=mock_client):
        sql = FastApiTool().generate_sql("How many customers?", "CREATE TABLE customer (id INT);")

    assert "SELECT" in sql
