"""Unit tests for FastApiInferenceClient (mocked HTTP)."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from tool.core.activity_logger import ActivityLogger
from tool.core.inference.fastapi_client import FastApiInferenceClient, format_timeout_error
from tool.core.settings_store import FastApiSettings


def test_format_timeout_error_includes_seconds():
    exc = httpx.ReadTimeout("The read operation timed out")
    assert format_timeout_error(exc, 15) == "The read operation timed out (timeout: 15 sec)"


def test_format_timeout_error_passthrough_for_other_errors():
    assert format_timeout_error(RuntimeError("connection refused"), 15) == "connection refused"


def test_generate_sql_raises_timeout_with_seconds():
    cfg = FastApiSettings(base_url="http://localhost:8000/v1", model="codegen-text2sql", timeout_sec=15)
    client = FastApiInferenceClient(cfg)

    with patch("tool.core.inference.fastapi_client.httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.side_effect = httpx.ReadTimeout("The read operation timed out")
        mock_client_cls.return_value = mock_client

        with pytest.raises(RuntimeError, match=r"timeout: 15 sec"):
            client.generate_sql("prompt text")


def test_generate_sql_extracts_from_response():
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "SELECT id FROM users WHERE active = 1"}}]
    }

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.post.return_value = mock_response

    cfg = FastApiSettings(base_url="http://localhost:8000/v1", model="codegen-text2sql")
    logger = ActivityLogger()

    with patch("tool.core.inference.fastapi_client.httpx.Client", return_value=mock_client):
        client = FastApiInferenceClient(cfg, logger=logger)
        sql = client.generate_sql("prompt text")

    assert "SELECT" in sql
    assert "users" in sql
    sql_event = next(e for e in logger.events if e.event == "sql_generated")
    assert sql_event.details["sql"] == sql
