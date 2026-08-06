"""Tests for Ask Agent chat."""

from unittest import mock

from agent.repo_ask_chat import chat_ask_generator


def test_ask_requires_repo_root_for_explain():
    history = []
    state = {}
    updates = list(chat_ask_generator("what is this?", history, state, "", max_files=5))
    assert updates
    assert "Project root" in updates[-1]["history"][-1]["content"]


def test_ask_nl_code_without_repo_root():
    history = []
    state = {}
    with mock.patch(
        "agent.repo_ask_chat.codegen_generate", return_value="def hello():\n    return 1"
    ):
        updates = list(
            chat_ask_generator(
                "Give me a program that converts Java to Python",
                history,
                state,
                "",
                max_files=5,
            )
        )
    final = updates[-1]["history"][-1]["content"]
    assert "```python" in final
    assert "Project root" not in final


def test_ask_parser_prompt_without_repo_root():
    history = []
    state = {}
    with mock.patch(
        "agent.repo_ask_chat.codegen_generate",
        return_value="import openpyxl\n\ndef read_rows(path):\n    ...",
    ):
        updates = list(
            chat_ask_generator(
                "Write a parser that reads the excel sheet row by row",
                history,
                state,
                "",
                max_files=5,
            )
        )
    final = updates[-1]["history"][-1]["content"]
    assert "```python" in final
    assert "Project root" not in final


def test_ask_nested_file_by_name(tmp_path):
    nested = tmp_path / "src" / "main" / "java"
    nested.mkdir(parents=True)
    (nested / "RepositoryLoader.java").write_text(
        "public class RepositoryLoader {}", encoding="utf-8"
    )
    (tmp_path / "A.java").write_text("class A {}", encoding="utf-8")

    history = []
    state = {}
    with mock.patch("agent.repo_ask_chat.codegen_generate", return_value="Loader class."):
        updates = list(
            chat_ask_generator(
                "explain RepositoryLoader.java",
                history,
                state,
                str(tmp_path),
                max_files=1,
            )
        )
    assert "Loader" in updates[-1]["history"][-1]["content"]
    assert len(updates[-1]["session_state"]["sources_cache"]) == 1
    assert "RepositoryLoader" in updates[-1]["session_state"]["sources_cache"][0]["name"]
    assert "RepositoryLoader.java" in updates[-1]["session_state"]["active_files"][0]


def test_ask_indexes_and_answers(tmp_path):
    d = tmp_path / "src"
    d.mkdir()
    (d / "Main.java").write_text("public class Main {}", encoding="utf-8")

    history = []
    state = {}
    with mock.patch("agent.repo_ask_chat.codegen_generate", return_value="This is Main."):
        updates = list(
            chat_ask_generator("explain Main", history, state, str(tmp_path), max_files=5)
        )
    assert updates[-1]["session_state"]["state"] == "qa"
    assert "Main" in updates[-1]["history"][-1]["content"]


def test_ask_follow_up_uses_cache(tmp_path):
    (tmp_path / "Main.java").write_text("public class Main {}", encoding="utf-8")
    (tmp_path / "Other.java").write_text("public class Other {}", encoding="utf-8")
    history = []
    state = {
        "state": "qa",
        "repo_root": str(tmp_path),
        "active_files": ["Main.java"],
        "sources_cache": [
            {"name": "Main.java", "language": "java", "snippet": "class Main", "ast_summary": ""},
            {"name": "Other.java", "language": "java", "snippet": "class Other", "ast_summary": ""},
        ],
    }
    with mock.patch("agent.repo_ask_chat.codegen_generate", return_value="Follow up answer."):
        updates = list(
            chat_ask_generator("what methods in Main.java?", history, state, str(tmp_path), max_files=5)
        )
    assert "Follow up" in updates[-1]["history"][-1]["content"]
    assert updates[-1]["history"][-1]["content"] != "Thinking..."


def test_ask_follow_up_reuses_active_files(tmp_path):
    (tmp_path / "Main.java").write_text("public class Main {}", encoding="utf-8")
    (tmp_path / "Other.java").write_text("public class Other {}", encoding="utf-8")
    history = []
    state = {
        "state": "qa",
        "repo_root": str(tmp_path),
        "active_files": ["Main.java"],
        "sources_cache": [
            {"name": "Main.java", "language": "java", "snippet": "class Main", "ast_summary": ""},
            {"name": "Other.java", "language": "java", "snippet": "class Other", "ast_summary": ""},
        ],
    }
    with mock.patch("agent.repo_ask_chat.codegen_generate", return_value="Follow up answer."):
        updates = list(
            chat_ask_generator("what does it do?", history, state, str(tmp_path), max_files=5)
        )
    assert "Follow up" in updates[-1]["history"][-1]["content"]
    assert state["active_files"] == ["Main.java"]


def test_ask_multiple_selected_files(tmp_path):
    (tmp_path / "A.java").write_text("public class A {}", encoding="utf-8")
    (tmp_path / "B.java").write_text("public class B {}", encoding="utf-8")
    history = []
    state = {"active_files": ["A.java", "B.java"]}
    prompts: list[str] = []

    def fake_generate(prompt, **kwargs):
        prompts.append(prompt)
        return f"Explanation for {len(prompts)}."

    with mock.patch("agent.repo_ask_chat.codegen_generate", side_effect=fake_generate):
        updates = list(
            chat_ask_generator(
                "explain the selected files",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )
    assert len(updates[-1]["session_state"]["sources_cache"]) == 2
    assert len(prompts) == 2
    assert "Explain what `A.java` does" in prompts[0] or "plain documentation for `A.java`" in prompts[0]
    assert "plain documentation for `B.java`" in prompts[1] or "Explain what `B.java` does" in prompts[1]
    assert "Structure:" not in prompts[0]
    assert "explain the selected files" not in prompts[0].lower()
    final = updates[-1]["history"][-1]["content"]
    assert "**Selected files (2):**" in final
    assert final.count("The selected files are") == 0
    assert "### A.java" in final
    assert "### B.java" in final
    assert updates[-1]["session_state"]["active_files"] == ["A.java", "B.java"]


def test_ask_four_selected_files_all_in_prompt(tmp_path):
    paths = [
        "mini-git/src/main/java/com/example/LogCommand.java",
        "mini-git/src/main/java/com/example/Command.java",
        "mini-git/src/main/java/com/example/CommandParser.java",
        "mini-git/src/main/java/com/example/Commit.java",
    ]
    for i, rel in enumerate(paths):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"public class File{i} {{}}", encoding="utf-8")

    history = []
    state = {"active_files": paths}
    prompts: list[str] = []

    def fake_generate(prompt, **kwargs):
        prompts.append(prompt)
        return f"Details for call {len(prompts)}."

    with mock.patch("agent.repo_ask_chat.codegen_generate", side_effect=fake_generate):
        updates = list(
            chat_ask_generator(
                "explain the selected files",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )
    assert len(updates[-1]["session_state"]["sources_cache"]) == 4
    assert len(prompts) == 4
    final = updates[-1]["history"][-1]["content"]
    assert "**Selected files (4):**" in final
    assert final.count("The selected files are") == 0
    for rel in paths:
        assert rel in final
    assert "### LogCommand.java" in final or "### Commit.java" in final


def test_ask_gen_python_in_chat(tmp_path):
    history = []
    state = {}
    with mock.patch(
        "agent.repo_ask_chat.codegen_generate", return_value="def hello():\n    return 'hi'"
    ):
        updates = list(
            chat_ask_generator(
                "python: hello world function",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )
    final = updates[-1]["history"][-1]["content"]
    assert "```python" in final
    assert "def hello()" in final
    assert not updates[-1]["session_state"].get("pending_writes")


def test_ask_gen_java_in_chat(tmp_path):
    history = []
    state = {}
    with mock.patch(
        "agent.repo_ask_chat.codegen_generate", return_value="public class Main {}"
    ):
        updates = list(
            chat_ask_generator(
                "java: simple class",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )
    final = updates[-1]["history"][-1]["content"]
    assert "```java" in final
    assert "public class Main" in final
    assert not updates[-1]["session_state"].get("pending_writes")


def test_ask_convert_selected_stays_explain(tmp_path):
    (tmp_path / "A.java").write_text("public class A {}", encoding="utf-8")
    (tmp_path / "B.java").write_text("public class B {}", encoding="utf-8")
    history = []
    state = {"active_files": ["A.java", "B.java"]}
    with mock.patch("agent.repo_ask_chat.codegen_generate", return_value="Class A docs."):
        updates = list(
            chat_ask_generator(
                "convert the selected files",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )
    assert not updates[-1]["session_state"].get("pending_writes")
    assert len(updates[-1]["session_state"]["sources_cache"]) == 2


def test_ask_program_request_ignores_stale_context(tmp_path):
    java = tmp_path / "CommandParser.java"
    java.write_text("public class CommandParser {}", encoding="utf-8")
    history = []
    state = {
        "state": "qa",
        "repo_root": str(tmp_path),
        "active_files": ["CommandParser.java"],
        "sources_cache": [
            {
                "name": "CommandParser.java",
                "language": "java",
                "snippet": "public class CommandParser {}",
                "ast_summary": "",
            }
        ],
    }
    prompts: list[str] = []

    def fake_generate(prompt, **kwargs):
        prompts.append(prompt)
        return "def java_to_python(src: str) -> str:\n    return src"

    with mock.patch("agent.repo_ask_chat.codegen_generate", side_effect=fake_generate):
        updates = list(
            chat_ask_generator(
                "Give me a program that converts Java to Python",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )
    final = updates[-1]["history"][-1]["content"]
    assert "```python" in final
    assert "java_to_python" in final
    assert len(prompts) == 1
    assert "Write Python for:" in prompts[0]
    assert "plain-English documentation" not in prompts[0]

