"""Tests for Debug Agent chat."""

from unittest import mock

from agent.repo_debug_chat import (
    _extract_debug_context,
    chat_debug_generator,
)


def test_extract_debug_context_strips_file_refs():
    ctx = _extract_debug_context("debug auth.py login fails with KeyError")
    assert "auth.py" not in ctx
    assert "KeyError" in ctx
    assert "login fails" in ctx


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


def test_validate_run_and_fix_passes_attempts_to_fix_fn():
    """Each static fix retry should pass an incrementing attempts counter."""
    from agent.nodes import attach_ast
    from agent.repo_migrate import _merge
    from agent.repo_utils import validate_run_and_fix_python
    from agent.state import initial_state

    recorded: list[int] = []

    def fake_fix(state):
        recorded.append(int(state.get("attempts") or 0))
        return {"python_code": state.get("python_code", ""), "trace": []}

    with mock.patch("agent.repo_utils._try_structural_syntax_repair", return_value=None):
        result = validate_run_and_fix_python(
            "print(2 +",
            "test context",
            3,
            _merge,
            attach_ast,
            fake_fix,
            initial_state,
            run_after_static=False,
        )
    assert result["static_ok"] is False
    assert recorded == [0, 1, 2]


def test_validate_run_and_fix_recovers_from_dangling_operator():
    """A partial fix (closing paren only) should be retried until code is valid."""
    from agent.nodes import attach_ast
    from agent.repo_migrate import _merge
    from agent.repo_utils import validate_run_and_fix_python
    from agent.state import initial_state

    fix_calls = {"n": 0}

    def fake_fix(state):
        fix_calls["n"] += 1
        if fix_calls["n"] == 1:
            return {"python_code": "print(2 + )", "trace": []}
        return {"python_code": "print(2 + 2)", "trace": []}

    result = validate_run_and_fix_python(
        "print(2 +",
        "test context",
        3,
        _merge,
        attach_ast,
        fake_fix,
        initial_state,
        run_after_static=False,
    )
    assert result["static_ok"] is True
    assert result["code"] == "print(2 + 2)"
    assert fix_calls["n"] == 2


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


def test_debug_passes_user_context_to_fix(tmp_path):
    runtime_bug = tmp_path / "auth.py"
    runtime_bug.write_text(
        "def divide(a, b):\n    return a / b\n\ndivide(10, 0)\n",
        encoding="utf-8",
    )
    history = []
    state = {"active_files": ["auth.py"]}

    with mock.patch("agent.repo_debug_chat.codegen_generate") as mock_llm, mock.patch(
        "agent.repo_debug_chat.validate_run_and_fix_python"
    ) as mock_fix:
        mock_llm.return_value = "Root cause: division by zero."
        mock_fix.return_value = {
            "code": "def divide(a, b):\n    if b == 0:\n        return None\n    return a / b\n\ndivide(10, 0)\n",
            "static_ok": True,
            "runtime_ok": True,
            "changed": True,
            "last_error": "",
            "trace_notes": [],
        }
        list(
            chat_debug_generator(
                "fix division by zero in auth.py",
                history,
                state,
                str(tmp_path),
                max_files=5,
                max_retries=3,
            )
        )
    context_arg = mock_fix.call_args[0][1]
    assert "division by zero" in context_arg
    mock_fix.assert_called_once()


def test_debug_diagnose_clean_file_with_description(tmp_path):
    good = tmp_path / "calc.py"
    good.write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
    history = []
    state = {"active_files": ["calc.py"]}

    with mock.patch("agent.repo_debug_chat.codegen_generate") as mock_llm:
        mock_llm.return_value = (
            "**Symptom**: add() subtracts instead of adding.\n"
            "**Root cause**: uses `-` instead of `+`."
        )
        updates = list(
            chat_debug_generator(
                "add returns wrong value",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )
    reply = "\n".join(m["content"] for m in updates[-1]["history"] if m["role"] == "assistant")
    assert "Symptom" in reply or "subtracts" in reply
    assert "### Diagnosis" in reply
    assert "fix it" in reply.lower()
    assert "see diagnosis above" not in reply.lower()
    assert updates[-1]["session_state"]["state"] == "debug_qa"
    assert updates[-1]["session_state"].get("sources_cache")
    assert updates[-1]["session_state"].get("last_diagnosis")


def test_debug_followup_uses_cached_sources(tmp_path):
    good = tmp_path / "calc.py"
    good.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    history = []
    state = {"active_files": ["calc.py"]}

    with mock.patch("agent.repo_debug_chat.codegen_generate") as mock_llm:
        mock_llm.side_effect = [
            "Initial diagnosis.",
            "Follow-up: check input types.",
        ]
        first = list(
            chat_debug_generator(
                "review calc.py",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )
        state = first[-1]["session_state"]
        history = first[-1]["history"]
        updates = list(
            chat_debug_generator(
                "what about negative numbers?",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )
    assert mock_llm.call_count == 2
    reply = "\n".join(m["content"] for m in updates[-1]["history"] if m["role"] == "assistant")
    assert "Follow-up" in reply or "negative" in reply.lower()


RUNTIME_BUG = (
    "def divide(a, b):\n"
    "    return a / b\n"
    "\n"
    "divide(10, 0)\n"
)

GUARDED_DIVIDE_FIX = (
    "def divide(a, b):\n"
    "    if b == 0:\n"
    "        return None\n"
    "    return a / b\n"
    "\n"
    "divide(10, 0)\n"
)

LAZY_DIVIDE_FIX = (
    "def divide(a, b):\n"
    "    return a / b\n"
)


def test_diagnose_shows_labeled_diagnosis(tmp_path):
    good = tmp_path / "calc.py"
    good.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    history = []
    state = {"active_files": ["calc.py"]}

    with mock.patch("agent.repo_debug_chat.codegen_generate") as mock_llm:
        mock_llm.return_value = "**Symptom**: none\n**Root cause**: n/a"
        updates = list(
            chat_debug_generator(
                "review calc.py for issues",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )
    reply = "\n".join(m["content"] for m in updates[-1]["history"] if m["role"] == "assistant")
    assert "### Diagnosis" in reply
    assert "Symptom" in reply


def test_review_query_no_auto_fix_on_clean_file(tmp_path):
    good = tmp_path / "calc.py"
    good.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    history = []
    state = {"active_files": ["calc.py"]}

    with mock.patch("agent.repo_debug_chat.codegen_generate") as mock_llm, mock.patch(
        "agent.repo_debug_chat.validate_run_and_fix_python"
    ) as mock_fix:
        mock_llm.return_value = "No issues found."
        updates = list(
            chat_debug_generator(
                "review calc.py for issues",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )
    mock_fix.assert_not_called()
    reply = "\n".join(m["content"] for m in updates[-1]["history"] if m["role"] == "assistant")
    assert "### Diagnosis" in reply
    assert "fix it" in reply.lower()
    assert "### Fix result" not in reply


def test_diagnose_preserves_diagnosis_after_mechanical_fix(tmp_path):
    bad = tmp_path / "runtime_bug.py"
    bad.write_text(RUNTIME_BUG, encoding="utf-8")
    history = []
    state = {"active_files": ["runtime_bug.py"]}

    with mock.patch("agent.repo_debug_chat.codegen_generate") as mock_llm, mock.patch(
        "agent.repo_debug_chat.validate_run_and_fix_python"
    ) as mock_fix:
        mock_llm.return_value = "**Symptom**: ZeroDivisionError\n**Root cause**: divide by zero"
        mock_fix.return_value = {
            "code": GUARDED_DIVIDE_FIX,
            "static_ok": True,
            "runtime_ok": True,
            "changed": True,
            "last_error": "",
            "trace_notes": [],
        }
        updates = list(
            chat_debug_generator(
                f"fix {bad.name}",
                history,
                state,
                str(tmp_path),
                max_files=5,
                max_retries=3,
            )
        )
    assistant_messages = [m["content"] for m in updates[-1]["history"] if m["role"] == "assistant"]
    assert any("### Diagnosis" in msg and "ZeroDivisionError" in msg for msg in assistant_messages)
    assert any("### Fix result" in msg for msg in assistant_messages)
    assert "see diagnosis above" not in "\n".join(assistant_messages).lower()


def test_is_inadequate_runtime_fix_detects_deleted_call():
    from agent.repo_utils import _is_inadequate_runtime_fix

    assert _is_inadequate_runtime_fix(
        RUNTIME_BUG,
        LAZY_DIVIDE_FIX,
        "ZeroDivisionError: division by zero",
    )
    assert not _is_inadequate_runtime_fix(
        RUNTIME_BUG,
        GUARDED_DIVIDE_FIX,
        "ZeroDivisionError: division by zero",
    )


def test_is_inadequate_runtime_fix_detects_nameerror_deletion():
    from agent.repo_utils import _is_inadequate_runtime_fix

    original = "print(missing)\n"
    lazy = "\n"
    fixed = "missing = 0\nprint(missing)\n"
    err = 'Traceback (most recent call last):\n  File "<string>", line 1, in <module>\nNameError: name \'missing\' is not defined'
    assert _is_inadequate_runtime_fix(original, lazy, err)
    assert not _is_inadequate_runtime_fix(original, fixed, err)


def test_is_inadequate_runtime_fix_detects_keyerror_deletion():
    from agent.repo_utils import _is_inadequate_runtime_fix

    original = "d = {}\nprint(d['key'])\n"
    lazy = "d = {}\n"
    fixed = "d = {'key': 1}\nprint(d['key'])\n"
    err = 'Traceback (most recent call last):\n  File "<string>", line 2, in <module>\nKeyError: \'key\''
    assert _is_inadequate_runtime_fix(original, lazy, err)
    assert not _is_inadequate_runtime_fix(original, fixed, err)


def test_parse_traceback_context_extracts_line_and_type():
    from agent.repo_utils import _format_traceback_hint

    err = (
        'Traceback (most recent call last):\n'
        '  File "<string>", line 4, in <module>\n'
        '    divide(10, 0)\n'
        'ZeroDivisionError: division by zero'
    )
    hint = _format_traceback_hint(err, RUNTIME_BUG)
    assert "ZeroDivisionError" in hint
    assert "line: 4" in hint or "Traceback line: 4" in hint
    assert "divide(10, 0)" in hint


def test_validate_run_and_fix_rejects_silent_passing_fix():
    from agent.nodes import attach_ast
    from agent.repo_migrate import _merge
    from agent.repo_utils import validate_run_and_fix_python
    from agent.state import initial_state

    fix_calls = {"n": 0}

    def fake_fix(state):
        fix_calls["n"] += 1
        return {"python_code": LAZY_DIVIDE_FIX, "trace": []}

    run_calls = {"n": 0}

    def fake_run(code, timeout=10):
        run_calls["n"] += 1
        if "divide(10, 0)" in code and "if b == 0" not in code:
            return {
                "stdout": "",
                "stderr": (
                    'Traceback (most recent call last):\n'
                    '  File "<string>", line 4, in <module>\n'
                    '    divide(10, 0)\n'
                    "ZeroDivisionError: division by zero"
                ),
                "passed": False,
                "exit_ok": False,
            }
        return {"stdout": "", "stderr": "", "passed": True, "exit_ok": True}

    result = validate_run_and_fix_python(
        RUNTIME_BUG,
        "Fix runtime error",
        2,
        _merge,
        attach_ast,
        fake_fix,
        initial_state,
        run_fn=fake_run,
    )
    assert result["runtime_ok"] is False
    assert fix_calls["n"] >= 1


def test_validate_run_and_fix_zero_division():
    from agent.nodes import attach_ast
    from agent.repo_migrate import _merge
    from agent.repo_utils import validate_run_and_fix_python
    from agent.state import initial_state

    fix_calls = {"n": 0}

    def fake_fix(state):
        fix_calls["n"] += 1
        if fix_calls["n"] == 1:
            return {"python_code": LAZY_DIVIDE_FIX, "trace": []}
        return {"python_code": GUARDED_DIVIDE_FIX, "trace": []}

    run_calls = {"n": 0}

    def fake_run(code, timeout=10):
        run_calls["n"] += 1
        if "divide(10, 0)" in code and "if b == 0" not in code:
            return {
                "stdout": "",
                "stderr": "ZeroDivisionError: division by zero",
                "passed": False,
                "exit_ok": False,
            }
        return {"stdout": "", "stderr": "", "passed": True, "exit_ok": True}

    result = validate_run_and_fix_python(
        RUNTIME_BUG,
        "Fix division by zero",
        3,
        _merge,
        attach_ast,
        fake_fix,
        initial_state,
        run_fn=fake_run,
    )
    assert result["static_ok"] is True
    assert result["runtime_ok"] is True
    assert "divide(10, 0)" in result["code"]
    assert "if b == 0" in result["code"]
    assert fix_calls["n"] >= 2


def test_diagnosis_passed_to_fix_context(tmp_path):
    bad = tmp_path / "broken.py"
    bad.write_text("print(2 +", encoding="utf-8")
    history = []
    state = {"active_files": ["broken.py"]}

    with mock.patch("agent.repo_debug_chat.codegen_generate") as mock_llm, mock.patch(
        "agent.repo_debug_chat.validate_run_and_fix_python"
    ) as mock_fix:
        mock_llm.return_value = (
            "**Suggested fix**: complete the expression as print(2 + 2)."
        )
        mock_fix.return_value = {
            "code": "print(2 + 2)",
            "static_ok": True,
            "runtime_ok": True,
            "changed": True,
            "last_error": "",
            "trace_notes": [],
        }
        list(
            chat_debug_generator(
                f"fix {bad.name}",
                history,
                state,
                str(tmp_path),
                max_files=5,
                max_retries=3,
            )
        )
    context_arg = mock_fix.call_args[0][1]
    assert "Prior diagnosis" in context_arg
    assert "Suggested fix" in context_arg


def test_failed_static_fix_not_queued(tmp_path):
    bad = tmp_path / "broken.py"
    bad.write_text("print(2 +", encoding="utf-8")
    history = []
    state = {"active_files": ["broken.py"]}

    with mock.patch("agent.repo_debug_chat.codegen_generate") as mock_llm, mock.patch(
        "agent.repo_debug_chat.validate_run_and_fix_python"
    ) as mock_fix:
        mock_llm.return_value = "Incomplete expression."
        mock_fix.return_value = {
            "code": "print(2 + )",
            "static_ok": False,
            "runtime_ok": False,
            "changed": True,
            "last_error": "SyntaxError: invalid syntax",
            "trace_notes": ["Static validation failed after 3 fix attempt(s)."],
        }
        updates = list(
            chat_debug_generator(
                f"fix {bad.name}",
                history,
                state,
                str(tmp_path),
                max_files=5,
                max_retries=3,
            )
        )
    assert not updates[-1].get("show_action_buttons")
    assert not updates[-1]["session_state"].get("pending_writes")


def test_is_stagnant_static_fix_rejects_paren_only_change():
    from agent.repo_utils import _is_stagnant_static_fix
    from agent.tools import validate_python_code

    before = "print(2 +"
    candidate = "print(2 + )"
    err = validate_python_code.invoke({"code": before})
    assert _is_stagnant_static_fix(before, candidate, err)


def test_try_structural_syntax_repair_dangling_operator():
    from agent.repo_utils import _try_structural_syntax_repair
    from agent.tools import validate_python_code

    err = validate_python_code.invoke({"code": "print(2 + )"})
    repaired = _try_structural_syntax_repair("print(2 + )", err)
    assert repaired is not None
    assert "2+2" in repaired.replace(" ", "")


def test_validate_run_and_fix_uses_structural_fallback():
    from agent.nodes import attach_ast
    from agent.repo_migrate import _merge
    from agent.repo_utils import validate_run_and_fix_python
    from agent.state import initial_state

    def always_bad_fix(state):
        return {"python_code": "print(2 + )", "trace": []}

    result = validate_run_and_fix_python(
        "print(2 + )",
        "fix syntax",
        1,
        _merge,
        attach_ast,
        always_bad_fix,
        initial_state,
        run_after_static=False,
    )
    assert result["static_ok"] is True
    assert "2+2" in result["code"].replace(" ", "")


def test_fix_python_escalates_on_later_attempts():
    from agent.nodes import fix_python

    state = {
        "nl_prompt": "Fix the code",
        "python_code": "print(2 + )",
        "stderr": "SyntaxError",
        "stdout": "",
        "unit": "auto",
        "ast_info": "",
        "attempts": 2,
        "max_retries": 3,
    }
    with mock.patch("agent.nodes.fix_generate") as mock_fix_gen:
        mock_fix_gen.return_value = "print(2 + 2)"
        fix_python(state)
    mock_fix_gen.assert_called_once()
    assert mock_fix_gen.call_args.kwargs.get("attempts") == 2
