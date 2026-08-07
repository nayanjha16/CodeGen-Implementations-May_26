"""Tests for Code Agent LangGraph."""

from __future__ import annotations

from unittest import mock

import pytest


@pytest.fixture(autouse=True)
def _reset_graph():
    from agent.code_graph import reset_code_graph

    reset_code_graph()
    yield
    reset_code_graph()


def test_code_graph_missing_repo():
    from agent.code_graph import code_turn

    result = code_turn("python: hi", [], {}, "")
    assert result.get("done")
    assert "Project root" in result.get("answer", "")


def test_code_graph_gen_python(tmp_path):
    from agent.code_graph import code_turn

    with mock.patch(
        "agent.repo_code_chat.codegen_generate", return_value="def f():\n    return 1"
    ), mock.patch(
        "agent.repo_code_chat.validate_and_fix_python", side_effect=lambda c, *a, **k: c
    ), mock.patch(
        "agent.repo_code_chat.add_python_comments", side_effect=lambda c: c
    ):
        result = code_turn("python: factorial", [], {}, str(tmp_path), max_retries=0)
    assert result.get("show_action_buttons")
    assert "Generated" in result.get("answer", "")


def test_code_graph_migrate_completes(tmp_path):
    from agent.code_graph import code_turn

    nested = tmp_path / "src" / "main"
    nested.mkdir(parents=True)
    java = nested / "RepositoryLoader.java"
    java.write_text("public class RepositoryLoader {}", encoding="utf-8")

    with mock.patch(
        "agent.repo_code_chat.codegen_generate",
        return_value="class RepositoryLoader:\n    pass",
    ), mock.patch(
        "agent.repo_code_chat.validate_and_fix_python", side_effect=lambda c, *a, **k: c
    ), mock.patch(
        "agent.code_nodes.add_python_comments", side_effect=lambda c: c
    ):
        result = code_turn(
            "RepositoryLoader.java", [], {}, str(tmp_path), max_retries=0, max_files=5
        )

    assert result.get("show_action_buttons")
    assert result["session_state"]["state"] == "review"
    assert "Conversion complete" in result.get("answer", "")
    pending = result["session_state"].get("pending_writes") or []
    assert any("RepositoryLoader" in p.get("name", "") for p in pending)
