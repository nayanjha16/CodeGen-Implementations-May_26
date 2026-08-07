"""Tests for Debug Agent LangGraph."""

from __future__ import annotations

from unittest import mock

import pytest


@pytest.fixture(autouse=True)
def _reset_graph():
    from agent.debug_graph import reset_debug_graph

    reset_debug_graph()
    yield
    reset_debug_graph()


def test_debug_graph_scan_clean(tmp_path):
    (tmp_path / "ok.py").write_text("x = 1\n", encoding="utf-8")
    from agent.debug_graph import debug_turn

    result = debug_turn("scan", [], {}, str(tmp_path), max_files=5)
    assert "No issues" in result.get("answer", "")


def test_debug_graph_fix_queues(tmp_path):
    bad = tmp_path / "bad.py"
    bad.write_text("print(2 +", encoding="utf-8")
    from agent.debug_graph import debug_turn

    with mock.patch("agent.repo_debug_chat.validate_run_and_fix_python") as mock_fix:
        mock_fix.return_value = {
            "code": "print(2 + 2)",
            "static_ok": True,
            "runtime_ok": True,
            "changed": True,
            "last_error": "",
        }
        result = debug_turn(f"fix {bad.name}", [], {}, str(tmp_path), max_retries=3)
    assert result.get("show_action_buttons")
    pending = result["session_state"].get("pending_writes", [])
    assert pending
    assert "print(2 + 2)" in pending[0]["content"]
