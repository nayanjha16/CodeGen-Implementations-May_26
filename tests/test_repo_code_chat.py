"""Tests for Code Agent chat."""

from pathlib import Path
from unittest import mock

from agent.repo_code_chat import chat_code_generator
from agent.repo_utils import pending_to_review_data


def _assert_migrate_complete(updates, history):
    assert updates[-1].get("show_action_buttons")
    assert updates[-1]["session_state"]["state"] == "review"
    assert any(
        "Conversion complete" in m.get("content", "")
        for m in history
        if m.get("role") == "assistant"
    )


def test_code_gen_python_queues_write(tmp_path):
    history = []
    state = {}
    with mock.patch("agent.repo_code_chat.codegen_generate", return_value="def f():\n    return 1"), \
         mock.patch("agent.repo_code_chat.validate_and_fix_python", side_effect=lambda c, *a, **k: c), \
         mock.patch("agent.repo_code_chat.add_python_comments", side_effect=lambda c: c):
        updates = list(
            chat_code_generator(
                "python: factorial function",
                history,
                state,
                str(tmp_path),
                max_retries=0,
                max_files=5,
            )
        )
    assert updates[-1].get("show_action_buttons")
    pending = pending_to_review_data(updates[-1]["session_state"])
    assert pending
    assert pending[0]["path"].endswith(".py")


def test_code_gen_java_queues_write(tmp_path):
    history = []
    state = {}
    with mock.patch(
        "agent.repo_code_chat.codegen_generate", return_value="public class Main {}"
    ):
        updates = list(
            chat_code_generator(
                "java: simple class",
                history,
                state,
                str(tmp_path),
                max_retries=0,
                max_files=5,
            )
        )
    assert updates[-1].get("show_action_buttons")
    pending = pending_to_review_data(updates[-1]["session_state"])
    assert pending
    assert pending[0]["path"].endswith(".java")


def test_code_migrate_java(tmp_path):
    java = tmp_path / "Main.java"
    java.write_text("public class Main {}", encoding="utf-8")

    history = []
    state = {}
    with mock.patch("agent.repo_code_chat.codegen_generate", return_value="class Main:\n    pass"), \
         mock.patch("agent.repo_code_chat.validate_and_fix_python", side_effect=lambda c, *a, **k: c), \
         mock.patch("agent.repo_code_chat.add_python_comments", side_effect=lambda c: c):
        updates = list(
            chat_code_generator(
                f"migrate {java.name}",
                history,
                state,
                str(tmp_path),
                max_retries=0,
                max_files=5,
            )
        )
    pending = pending_to_review_data(updates[-1]["session_state"])
    assert any("Main" in p["name"] for p in pending)
    assert updates[-1]["session_state"]["active_files"] == ["Main.java"]
    _assert_migrate_complete(updates, history)


def test_code_migrate_nested_java(tmp_path):
    nested = tmp_path / "src" / "main"
    nested.mkdir(parents=True)
    java = nested / "RepositoryLoader.java"
    java.write_text("public class RepositoryLoader {}", encoding="utf-8")

    history = []
    state = {}
    with mock.patch("agent.repo_code_chat.codegen_generate", return_value="class RepositoryLoader:\n    pass"), \
         mock.patch("agent.repo_code_chat.validate_and_fix_python", side_effect=lambda c, *a, **k: c), \
         mock.patch("agent.repo_code_chat.add_python_comments", side_effect=lambda c: c):
        updates = list(
            chat_code_generator(
                "RepositoryLoader.java",
                history,
                state,
                str(tmp_path),
                max_retries=0,
                max_files=5,
            )
        )
    pending = pending_to_review_data(updates[-1]["session_state"])
    assert any("RepositoryLoader" in p["name"] for p in pending)
    assert "RepositoryLoader.java" in updates[-1]["session_state"]["active_files"][0]
    _assert_migrate_complete(updates, history)


def test_code_migrate_multiple_selected(tmp_path):
    (tmp_path / "A.java").write_text("public class A {}", encoding="utf-8")
    (tmp_path / "B.java").write_text("public class B {}", encoding="utf-8")

    history = []
    state = {"active_files": ["A.java", "B.java"]}
    with mock.patch("agent.repo_code_chat.codegen_generate", return_value="class A:\n    pass"), \
         mock.patch("agent.repo_code_chat.validate_and_fix_python", side_effect=lambda c, *a, **k: c), \
         mock.patch("agent.repo_code_chat.add_python_comments", side_effect=lambda c: c):
        updates = list(
            chat_code_generator(
                "migrate selected files",
                history,
                state,
                str(tmp_path),
                max_retries=0,
                max_files=5,
            )
        )
    pending = pending_to_review_data(updates[-1]["session_state"])
    names = {p["name"] for p in pending}
    assert "A.java" in names or any("A" in n for n in names)
    assert len(pending) == 2
    assert set(updates[-1]["session_state"]["active_files"]) == {"A.java", "B.java"}
    _assert_migrate_complete(updates, history)


def test_code_convert_selected_files(tmp_path):
    (tmp_path / "A.java").write_text("public class A {}", encoding="utf-8")
    (tmp_path / "B.java").write_text("public class B {}", encoding="utf-8")
    (tmp_path / "C.java").write_text("public class C {}", encoding="utf-8")
    (tmp_path / "D.java").write_text("public class D {}", encoding="utf-8")

    history = []
    state = {"active_files": ["A.java", "B.java", "C.java", "D.java"]}
    with mock.patch("agent.repo_code_chat.codegen_generate", return_value="class A:\n    pass"), \
         mock.patch("agent.repo_code_chat.validate_and_fix_python", side_effect=lambda c, *a, **k: c), \
         mock.patch("agent.repo_code_chat.add_python_comments", side_effect=lambda c: c):
        updates = list(
            chat_code_generator(
                "convert the selected files",
                history,
                state,
                str(tmp_path),
                max_retries=0,
                max_files=5,
            )
        )
    pending = pending_to_review_data(updates[-1]["session_state"])
    paths = {p["path"] for p in pending}
    assert len(pending) == 4
    assert str(tmp_path / "A.py") in paths
    assert str(tmp_path / "B.py") in paths
    assert str(tmp_path / "C.py") in paths
    assert str(tmp_path / "D.py") in paths
    assert not any("generated_" in p for p in paths)
    _assert_migrate_complete(updates, history)


def test_code_convert_string_stays_gen_python(tmp_path):
    """NL Python requests should not be misrouted to migrate."""
    from agent.repo_utils import detect_code_task

    assert detect_code_task("convert string to int in python") == "gen_python"
    assert detect_code_task("convert string to int in python", ["A.java"]) == "gen_python"


def _seed_java_repo(tmp_path):
    for name in ("App.java", "Util.java", "Service.java"):
        (tmp_path / name).write_text(f"public class {name[:-5]} {{}}", encoding="utf-8")


def test_code_gen_singleton_java_repo(tmp_path):
    _seed_java_repo(tmp_path)
    history = []
    state = {}
    with mock.patch(
        "agent.repo_code_chat.codegen_generate",
        return_value="public class Singleton { private Singleton() {} }",
    ):
        updates = list(
            chat_code_generator(
                "generate singleton pattern",
                history,
                state,
                str(tmp_path),
                max_retries=0,
                max_files=5,
            )
        )
    pending = pending_to_review_data(updates[-1]["session_state"])
    assert pending
    assert pending[0]["path"].endswith("Singleton.java")


def test_code_gen_singleton_in_python_overrides_java_repo(tmp_path):
    _seed_java_repo(tmp_path)
    history = []
    state = {}
    with mock.patch(
        "agent.repo_code_chat.codegen_generate",
        return_value="class Singleton:\n    pass",
    ), mock.patch(
        "agent.repo_code_chat.validate_and_fix_python", side_effect=lambda c, *a, **k: c
    ), mock.patch(
        "agent.repo_code_chat.add_python_comments", side_effect=lambda c: c
    ):
        updates = list(
            chat_code_generator(
                "generate singleton pattern in python",
                history,
                state,
                str(tmp_path),
                max_retries=0,
                max_files=5,
            )
        )
    pending = pending_to_review_data(updates[-1]["session_state"])
    assert pending[0]["path"].endswith("singleton.py")


def test_code_gen_includes_repo_few_shot(tmp_path):
    _seed_java_repo(tmp_path)
    (tmp_path / "Singleton.java").write_text(
        "public class Singleton { private Singleton() {} }",
        encoding="utf-8",
    )
    prompts: list[str] = []

    def capture_prompt(prompt, **kwargs):
        prompts.append(prompt)
        return "public class Singleton {}"

    history = []
    state = {}
    with mock.patch("agent.repo_code_chat.codegen_generate", side_effect=capture_prompt):
        list(
            chat_code_generator(
                "generate singleton pattern",
                history,
                state,
                str(tmp_path),
                max_retries=0,
                max_files=5,
            )
        )
    assert prompts
    assert "Repository style reference" in prompts[0]
    assert "Singleton.java" in prompts[0]


def test_code_gen_java_similar_to_selected(tmp_path):
    nested = tmp_path / "src" / "exceptions"
    nested.mkdir(parents=True)
    ref = nested / "ExistingRepositoryException.java"
    ref.write_text(
        "public class ExistingRepositoryException extends RuntimeException {}",
        encoding="utf-8",
    )
    prompts: list[str] = []

    def capture_prompt(prompt, **kwargs):
        prompts.append(prompt)
        return "public class ExistingBranchException extends RuntimeException {}"

    history = []
    state = {"active_files": ["src/exceptions/ExistingRepositoryException.java"]}
    with mock.patch("agent.repo_code_chat.codegen_generate", side_effect=capture_prompt):
        updates = list(
            chat_code_generator(
                "create ExistingBranchException similar to the file selected in Java",
                history,
                state,
                str(tmp_path),
                max_retries=0,
                max_files=5,
            )
        )
    assert "converting Java to Python" not in updates[1]["history"][-1]["content"]
    assert "generating java" in updates[1]["history"][-1]["content"].lower()
    pending = pending_to_review_data(updates[-1]["session_state"])
    assert pending
    assert pending[0]["path"].endswith("ExistingBranchException.java")
    assert Path(pending[0]["path"]).parent == nested
    assert prompts
    assert "ExistingRepositoryException.java" in prompts[0]
    assert "ExistingRepositoryException" in prompts[0]


def test_code_gen_python_similar_to_selected(tmp_path):
    nested = tmp_path / "handlers"
    nested.mkdir()
    ref = nested / "base_handler.py"
    ref.write_text("class BaseHandler:\n    pass\n", encoding="utf-8")
    history = []
    state = {"active_files": ["handlers/base_handler.py"]}
    with mock.patch(
        "agent.repo_code_chat.codegen_generate",
        return_value="class BarHandler:\n    pass\n",
    ), mock.patch(
        "agent.repo_code_chat.validate_and_fix_python", side_effect=lambda c, *a, **k: c
    ), mock.patch(
        "agent.repo_code_chat.add_python_comments", side_effect=lambda c: c
    ):
        updates = list(
            chat_code_generator(
                "create BarHandler similar to the selected file",
                history,
                state,
                str(tmp_path),
                max_retries=0,
                max_files=5,
            )
        )
    pending = pending_to_review_data(updates[-1]["session_state"])
    assert pending
    assert pending[0]["path"].endswith("bar_handler.py")
    assert Path(pending[0]["path"]).parent == nested

