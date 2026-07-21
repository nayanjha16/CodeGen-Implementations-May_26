from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from codegen_rag.app.api_client import APIClient, APIClientError


def _mock_response(status_code: int, json_body: dict) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_body
    mock.text = str(json_body)
    return mock


@patch("codegen_rag.app.api_client.requests.post")
def test_generate_returns_parsed_json(mock_post):
    mock_post.return_value = _mock_response(200, {"code": "def f(): pass", "language": "python"})
    client = APIClient(base_url="http://testserver")
    result = client.generate("do a thing")
    assert result["code"] == "def f(): pass"
    mock_post.assert_called_once()
    called_url = mock_post.call_args[0][0]
    assert called_url == "http://testserver/generate"


@patch("codegen_rag.app.api_client.requests.post")
def test_error_status_raises_api_client_error_with_detail(mock_post):
    mock_post.return_value = _mock_response(404, {"detail": "No database found for db_id='x'"})
    client = APIClient(base_url="http://testserver")
    with pytest.raises(APIClientError, match="No database found"):
        client.sql("how many?", "x")


@patch("codegen_rag.app.api_client.requests.post")
def test_connection_error_raises_api_client_error(mock_post):
    mock_post.side_effect = requests.ConnectionError("refused")
    client = APIClient(base_url="http://unreachable:9999")
    with pytest.raises(APIClientError, match="Could not reach backend"):
        client.document("def f(): pass")


@patch("codegen_rag.app.api_client.requests.get")
def test_health_check_success(mock_get):
    mock_get.return_value = _mock_response(200, {"status": "ok", "version": "0.1.0"})
    client = APIClient(base_url="http://testserver")
    result = client.health()
    assert result["status"] == "ok"


@patch("codegen_rag.app.api_client.requests.get")
def test_health_check_failure_raises(mock_get):
    mock_get.return_value = _mock_response(500, {"detail": "boom"})
    client = APIClient(base_url="http://testserver")
    with pytest.raises(APIClientError):
        client.health()


@patch("codegen_rag.app.api_client.requests.post")
def test_translate_passes_all_parameters(mock_post):
    mock_post.return_value = _mock_response(
        200, {"translated_code": "public class F {}", "source_language": "python", "target_language": "java"}
    )
    client = APIClient(base_url="http://testserver")
    result = client.translate("def f(): pass", source_language="python", target_language="java")
    assert result["translated_code"] == "public class F {}"
    payload = mock_post.call_args[1]["json"]
    assert payload == {
        "source_code": "def f(): pass",
        "source_language": "python",
        "target_language": "java",
    }


@patch("codegen_rag.app.api_client.requests.post")
def test_rag_passes_all_parameters(mock_post):
    mock_post.return_value = _mock_response(
        200, {"generation": "code", "retrieved_count": 3, "strategy": "hybrid", "top_k": 3, "used_llm": True}
    )
    client = APIClient(base_url="http://testserver")
    client.rag("query", top_k=3, strategy="hybrid", use_llm=True)
    payload = mock_post.call_args[1]["json"]
    assert payload == {"query": "query", "task": "program_synthesis", "top_k": 3, "strategy": "hybrid", "use_llm": True}
