"""Unit tests for FastApiInferenceClient (mocked HTTP)."""

from unittest.mock import MagicMock, patch

from tool.core.activity_logger import ActivityLogger
from tool.core.inference.fastapi_client import FastApiInferenceClient
from tool.core.settings_store import FastApiSettings


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
