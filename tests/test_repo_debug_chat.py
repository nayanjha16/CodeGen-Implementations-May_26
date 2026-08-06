"""Tests for Debug Agent chat."""

from unittest import mock

from agent.repo_debug_chat import chat_debug_generator


def test_debug_scan_clean(tmp_path):
    (tmp_path / "ok.py").write_text("x = 1\n", encoding="utf-8")
    history = []
    state = {}
    updates = list(chat_debug_generator("scan", history, state, str(tmp_path), max_files=5))
    assert "No issues" in updates[-1]["history"][-1]["content"]


def test_debug_scan_finds_syntax_error(tmp_path):
    (tmp_path / "bad.py").write_text("print(2 +", encoding="utf-8")
    history = []
    state = {}
    updates = list(chat_debug_generator("scan", history, state, str(tmp_path), max_files=5))
    assert "Found" in updates[-1]["history"][-1]["content"]
    assert updates[-1]["session_state"].get("scan_issues")


def test_debug_fix_queues(tmp_path):
    bad = tmp_path / "bad.py"
    bad.write_text("print(2 +", encoding="utf-8")
    history = []
    state = {}

    with mock.patch("agent.repo_debug_chat.validate_run_and_fix_python") as mock_fix:
        mock_fix.return_value = {
            "code": "print(2 + 2)",
            "static_ok": True,
            "runtime_ok": True,
            "changed": True,
            "last_error": "",
        }
        updates = list(
            chat_debug_generator(
                f"fix {bad.name}", history, state, str(tmp_path), max_files=5, max_retries=3
            )
        )
    assert updates[-1].get("show_action_buttons")
    pending = updates[-1]["session_state"].get("pending_writes", [])
    assert pending
    assert "print(2 + 2)" in pending[0]["content"]
    assert updates[-1]["session_state"]["active_files"] == ["bad.py"]
    mock_fix.assert_called_once()


def test_debug_fix_nested_py(tmp_path):
    nested = tmp_path / "services"
    nested.mkdir()
    bad = nested / "auth.py"
    bad.write_text("print(2 +", encoding="utf-8")
    history = []
    state = {}

    with mock.patch("agent.repo_debug_chat.validate_run_and_fix_python") as mock_fix:
        mock_fix.return_value = {
            "code": "print(2 + 2)",
            "static_ok": True,
            "runtime_ok": True,
            "changed": True,
            "last_error": "",
        }
        updates = list(
            chat_debug_generator("auth.py", history, state, str(tmp_path), max_files=1, max_retries=3)
        )
    assert updates[-1].get("show_action_buttons")
    pending = updates[-1]["session_state"].get("pending_writes", [])
    assert pending
    assert pending[0]["path"].endswith("auth.py")
    assert "auth.py" in updates[-1]["session_state"]["active_files"][0]


def test_debug_fix_multiple_selected(tmp_path):
    (tmp_path / "a.py").write_text("print(2 +", encoding="utf-8")
    (tmp_path / "b.py").write_text("print(3 +", encoding="utf-8")
    history = []
    state = {"active_files": ["a.py", "b.py"]}

    with mock.patch("agent.repo_debug_chat.validate_run_and_fix_python") as mock_fix:
        mock_fix.return_value = {
            "code": "print(2 + 2)",
            "static_ok": True,
            "runtime_ok": True,
            "changed": True,
            "last_error": "",
        }
        updates = list(
            chat_debug_generator(
                "fix selected", history, state, str(tmp_path), max_files=5, max_retries=3
            )
        )
    assert updates[-1].get("show_action_buttons")
    pending = updates[-1]["session_state"].get("pending_writes", [])
    assert len(pending) == 2
    assert set(updates[-1]["session_state"]["active_files"]) == {"a.py", "b.py"}
    assert mock_fix.call_count == 2


def test_debug_fix_all_migrated(tmp_path):
    (tmp_path / "a.py").write_text("print(2 +", encoding="utf-8")
    (tmp_path / "b.py").write_text("print(3 +", encoding="utf-8")
    history = []
    state = {"migrated_py_paths": ["a.py", "b.py"]}

    with mock.patch("agent.repo_debug_chat.validate_run_and_fix_python") as mock_fix:
        mock_fix.return_value = {
            "code": "print(1)",
            "static_ok": True,
            "runtime_ok": True,
            "changed": True,
            "last_error": "",
        }
        updates = list(
            chat_debug_generator(
                "fix all migrated",
                history,
                state,
                str(tmp_path),
                max_files=5,
                max_retries=3,
            )
        )
    assert updates[-1].get("show_action_buttons")
    assert mock_fix.call_count == 2


def test_debug_fix_retries_passed(tmp_path):
    bad = tmp_path / "bad.py"
    bad.write_text("print(2 +", encoding="utf-8")
    history = []
    state = {}

    with mock.patch("agent.repo_debug_chat.validate_run_and_fix_python") as mock_fix:
        mock_fix.return_value = {
            "code": "print(2 + 2)",
            "static_ok": True,
            "runtime_ok": True,
            "changed": True,
            "last_error": "",
        }
        list(
            chat_debug_generator(
                f"fix {bad.name}", history, state, str(tmp_path), max_files=5, max_retries=5
            )
        )
    assert mock_fix.call_args[0][2] == 5


def test_debug_runtime_fix_loop(tmp_path):
    """validate_run_and_fix_python runs runtime phase when static passes."""
    from agent.nodes import attach_ast, fix_python
    from agent.repo_migrate import _merge
    from agent.repo_utils import validate_run_and_fix_python
    from agent.state import initial_state

    fix_calls = {"n": 0}

    def fake_fix(state):
        fix_calls["n"] += 1
        code = "print('ok')" if fix_calls["n"] >= 1 else state.get("python_code", "")
        return {"python_code": code, "trace": []}

    run_calls = {"n": 0}

    def fake_run(code, timeout=10):
        run_calls["n"] += 1
        if run_calls["n"] == 1:
            return {"stdout": "", "stderr": "NameError: x", "passed": False, "exit_ok": False}
        return {"stdout": "ok\n", "stderr": "", "passed": True, "exit_ok": True}

    result = validate_run_and_fix_python(
        "print(x)",
        "test context",
        3,
        _merge,
        attach_ast,
        fake_fix,
        initial_state,
        run_fn=fake_run,
    )
    assert result["static_ok"] is True
    assert result["runtime_ok"] is True
    assert fix_calls["n"] >= 1
    assert run_calls["n"] >= 2


def test_debug_ambiguous_file(tmp_path):
    a = tmp_path / "pkg" / "utils.py"
    b = tmp_path / "other" / "utils.py"
    a.parent.mkdir(parents=True)
    b.parent.mkdir(parents=True)
    a.write_text("print(2 +", encoding="utf-8")
    b.write_text("print(3 +", encoding="utf-8")

    history = []
    state = {}
    updates = list(
        chat_debug_generator("utils.py", history, state, str(tmp_path), max_files=5)
    )
    reply = updates[-1]["history"][-1]["content"]
    assert "Multiple files match" in reply
