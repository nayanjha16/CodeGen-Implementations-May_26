"""Tests for Ask Agent LangGraph."""

from __future__ import annotations

from unittest import mock

import pytest


@pytest.fixture(autouse=True)
def _reset_graph():
    from agent.ask_graph import reset_ask_graph

    reset_ask_graph()
    yield
    reset_ask_graph()


def test_ask_graph_missing_repo():
    from agent.ask_graph import ask_turn

    result = ask_turn("what is this?", {}, {}, "")
    assert result.get("done")
    assert "Project root" in result.get("answer", "")


def test_ask_graph_inline_python():
    from agent.ask_graph import ask_turn

    with mock.patch("agent.repo_ask_chat.codegen_generate", return_value="def f(): pass"):
        result = ask_turn("python: hello world", [], {}, "/tmp")
    assert "```python" in result.get("answer", "")


def test_ask_graph_general_without_repo():
    from agent.ask_graph import ask_turn

    with mock.patch(
        "agent.repo_ask_chat.ask_generate",
        return_value="Authentication verifies identity.",
    ):
        result = ask_turn("explain authentication", [], {}, "")
    assert "authentication" in result.get("answer", "").lower()
