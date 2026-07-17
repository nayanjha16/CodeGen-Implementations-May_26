"""Unit tests for connection_tester (mocked)."""

from unittest.mock import MagicMock, patch

from tool.core.connection_tester import run_database_test, run_fastapi_test
from tool.core.settings_store import DatabaseConnection, FastApiSettings


def test_test_database_success(sample_connection: DatabaseConnection):
    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.execute.return_value.fetchone.return_value = ("PostgreSQL 16",)

    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_conn

    with patch("tool.core.connection_tester.create_engine", return_value=mock_engine):
        result = run_database_test(sample_connection)

    assert result.success is True
    assert result.latency_ms >= 0
    assert result.server_version == "PostgreSQL 16"


def test_test_database_failure(sample_connection: DatabaseConnection):
    with patch("tool.core.connection_tester.create_engine", side_effect=RuntimeError("connection refused")):
        result = run_database_test(sample_connection)
    assert result.success is False
    assert "connection refused" in (result.error or "")


def test_test_fastapi_success():
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"status": "ok", "router": {}}

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.return_value = mock_response

    cfg = FastApiSettings(health_url="http://localhost:8000/health")
    with patch("tool.core.connection_tester.httpx.Client", return_value=mock_client):
        result = run_fastapi_test(cfg)

    assert result.success is True
    assert result.details is not None


def test_test_fastapi_failure():
    with patch("tool.core.connection_tester.httpx.Client", side_effect=RuntimeError("timeout")):
        result = run_fastapi_test(FastApiSettings())
    assert result.success is False
