"""Tests for agent web API."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from agent.orchestration.state import AgentResult
from agent.web.app import app


def test_health_endpoint() -> None:
    client = TestClient(app)
    res = client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert "codegen_api_url" in body


def test_examples_endpoint() -> None:
    client = TestClient(app)
    res = client.get("/api/examples")
    assert res.status_code == 200
    examples = res.json()
    assert len(examples) >= 3
    assert examples[0]["id"]


def test_index_page() -> None:
    client = TestClient(app)
    res = client.get("/")
    assert res.status_code == 200
    assert "AI Database Agent" in res.text


@patch("agent.web.app.run_agent_graph")
def test_query_endpoint(mock_run: MagicMock) -> None:
    mock_run.return_value = AgentResult(
        answer="Iron Maiden has the most albums.",
        intent="text2sql",
        sql='SELECT "Name" FROM "Artist" LIMIT 1',
        rows=[{"Name": "Iron Maiden"}],
    )
    client = TestClient(app)
    res = client.post(
        "/api/query",
        json={"message": "Which artist has the most albums?", "intent": "text2sql"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["intent"] == "text2sql"
    assert "Iron Maiden" in body["answer"]
