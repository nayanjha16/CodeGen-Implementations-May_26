"""Stage 2 unit tests for CodeGen HTTP client (mocked)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from agent.clients.codegen_client import CodeGenClient
from agent.config.settings import AgentSettings, MongoSettings, PostgresSettings, StandaloneDatabaseSettings


def _settings() -> AgentSettings:
    return AgentSettings(
        postgres=PostgresSettings("localhost", 5432, "tend", "tend", "postgres"),
        mongo=MongoSettings("localhost", 27017, "tend", "tend"),
        demo=StandaloneDatabaseSettings("chinook", "chinook", "public", "chinook", None),
        codegen_api_url="https://example.test",
        codegen_api_key="",
        codegen_model="codegen-text2sql",
        codegen_timeout_sec=30,
        codegen_max_tokens=256,
        codegen_temperature=0.2,
        ollama_base_url="http://localhost:11434",
        ollama_model="gemma3:4b",
        database_profile="standalone",
        default_dataset="spider",
        max_result_rows=100,
        max_retries=3,
        query_timeout_ms=10000,
    )


def test_generate_sql_uses_intent_and_extracts_sql() -> None:
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "SELECT COUNT(*) FROM customers"}}]
    }
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.post.return_value = mock_response

    with patch("agent.clients.codegen_client.httpx.Client", return_value=mock_client):
        sql = CodeGenClient(_settings()).generate_sql(
            "How many customers?",
            "CREATE TABLE customers (id INT);",
        )

    assert sql.startswith("SELECT")
    payload = mock_client.post.call_args.kwargs["json"]
    assert payload["intent"] == "text2sql"
    assert "Question:" in payload["messages"][0]["content"]


def test_generate_sql_retry_appends_error_context() -> None:
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "SELECT 1"}}]
    }
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.post.return_value = mock_response

    with patch("agent.clients.codegen_client.httpx.Client", return_value=mock_client):
        CodeGenClient(_settings()).generate_sql(
            "How many customers?",
            "CREATE TABLE customers (id INT);",
            previous_sql="SELECT bad",
            db_error='relation "bad" does not exist',
        )

    prompt = mock_client.post.call_args.kwargs["json"]["messages"][0]["content"]
    assert "Previous SQL:" in prompt
    assert "Database error:" in prompt


def test_generate_nosql_intent() -> None:
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "db.customers.find({})"}}]
    }
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.post.return_value = mock_response

    with patch("agent.clients.codegen_client.httpx.Client", return_value=mock_client):
        nosql = CodeGenClient(_settings()).generate_nosql(
            "SELECT * FROM customers",
            "CREATE TABLE customers (id INT);",
        )

    assert nosql.startswith("db.")
    assert mock_client.post.call_args.kwargs["json"]["intent"] == "sql2nosql"


def test_health_ok() -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok"}
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.return_value = mock_response

    with patch("agent.clients.codegen_client.httpx.Client", return_value=mock_client):
        health = CodeGenClient(_settings()).health()

    assert health.ok is True


def test_post_chat_timeout_message() -> None:
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.post.side_effect = httpx.ReadTimeout("timed out")

    with patch("agent.clients.codegen_client.httpx.Client", return_value=mock_client):
        with pytest.raises(RuntimeError, match="timeout: 30 sec"):
            CodeGenClient(_settings()).generate_sql("q", "schema")
