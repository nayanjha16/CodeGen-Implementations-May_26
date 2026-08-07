"""Tests for Ask Agent chat."""

from unittest import mock

import pytest

from agent.ask_query_planner import (
    ANSWER_MODE_CLARIFY,
    ANSWER_MODE_DIRECT,
    ANSWER_MODE_INVENTORY,
    ANSWER_MODE_PER_FILE,
    AskPlan,
    OVERVIEW_RETRIEVAL_QUERY,
    apply_plan_heuristics,
)
from agent.repo_ask_chat import (
    _retrieve_sources,
    _sanitize_ask_response,
    chat_ask_generator,
    is_repo_scoped_question,
)


def _mock_plan(
    *,
    intent: str = "",
    retrieval: str = "",
    mode: str = ANSWER_MODE_DIRECT,
    inventory: bool = False,
    follow_up: bool = False,
):
    return AskPlan(
        intent_summary=intent or retrieval or "test intent",
        retrieval_query=retrieval or intent or "test query",
        answer_mode=mode,
        needs_repo_inventory=inventory,
        is_follow_up=follow_up,
    )


def _mock_rag_chunks(mock_pipeline, chunks: list[dict]) -> None:
    """Configure RAG pipeline mock for both retrieve and retrieve_overview."""
    mock_pipeline.return_value.retrieve.return_value = chunks
    mock_pipeline.return_value.retrieve_overview.return_value = chunks


def test_ask_requires_repo_root_for_explain():
    history = []
    state = {}
    updates = list(chat_ask_generator("what is this?", history, state, "", max_files=5))
    assert updates
    assert "Project root" in updates[-1]["history"][-1]["content"]


def test_is_repo_scoped_question():
    assert is_repo_scoped_question("what is this?")
    assert is_repo_scoped_question("explain singleton in this repo")
    assert is_repo_scoped_question("explain Main.java")
    assert is_repo_scoped_question("list files in the repo")
    assert is_repo_scoped_question("where is the auth module")
    assert not is_repo_scoped_question("explain authentication")
    assert not is_repo_scoped_question("what is singleton pattern")
    assert not is_repo_scoped_question("what is REST")
    assert not is_repo_scoped_question("explain Java inheritance")
    assert not is_repo_scoped_question("what is a list comprehension in Python")


def test_ask_general_without_repo_root():
    history = []
    state = {}
    with mock.patch(
        "agent.repo_ask_chat.ask_generate",
        return_value="Authentication verifies identity before granting access to resources.",
    ):
        updates = list(
            chat_ask_generator(
                "explain authentication",
                history,
                state,
                "",
                max_files=5,
            )
        )
    final = updates[-1]["history"][-1]["content"]
    assert "authentication" in final.lower()
    assert "Project root" not in final


def test_ask_sequential_general_questions_without_repo_root():
    """Regression: second non-RAG question should not prompt for project root."""
    history = []
    state = {}
    with mock.patch(
        "agent.repo_ask_chat.ask_generate",
        side_effect=[
            "The Singleton pattern ensures a class has only one instance.",
            "Authentication verifies identity before granting access to resources.",
        ],
    ):
        list(
            chat_ask_generator(
                "what is singleton pattern",
                history,
                state,
                "",
                max_files=5,
            )
        )
        updates = list(
            chat_ask_generator(
                "explain authentication",
                history,
                state,
                "",
                max_files=5,
            )
        )
    final = updates[-1]["history"][-1]["content"]
    assert "authentication" in final.lower()
    assert "Project root" not in final


def test_ask_follow_up_without_repo_root():
    history = []
    state = {}
    with mock.patch(
        "agent.repo_ask_chat.ask_generate",
        side_effect=[
            "The Singleton pattern ensures a class has only one instance.",
            "Use it when exactly one shared instance is required globally.",
        ],
    ):
        list(
            chat_ask_generator(
                "what is singleton pattern",
                history,
                state,
                "",
                max_files=5,
            )
        )
        updates = list(
            chat_ask_generator(
                "when should I use it?",
                history,
                state,
                "",
                max_files=5,
            )
        )
    final = updates[-1]["history"][-1]["content"]
    assert "instance" in final.lower()
    assert "Project root" not in final


def test_ask_ft_domain_without_repo_root():
    history = []
    state = {}
    with mock.patch(
        "agent.repo_ask_chat.ask_generate",
        return_value="The Singleton pattern ensures a class has only one instance.",
    ):
        updates = list(
            chat_ask_generator(
                "what is singleton pattern",
                history,
                state,
                "",
                max_files=5,
            )
        )
    final = updates[-1]["history"][-1]["content"]
    assert "Singleton" in final
    assert "Project root" not in final


def test_ask_java_inheritance_without_repo_root():
    history = []
    state = {}
    with mock.patch(
        "agent.repo_ask_chat.ask_generate",
        return_value="Java inheritance lets a subclass reuse and extend a superclass.",
    ):
        updates = list(
            chat_ask_generator(
                "explain Java inheritance",
                history,
                state,
                "",
                max_files=5,
            )
        )
    final = updates[-1]["history"][-1]["content"]
    assert "inheritance" in final.lower()
    assert "Project root" not in final


def test_ask_ft_domain_skips_rag_and_planner():
    history = []
    state = {}
    with (
        mock.patch(
            "agent.repo_ask_chat.ask_generate",
            return_value="The Facade pattern provides a simplified interface.",
        ),
        mock.patch("agent.repo_ask_chat.plan_ask_query") as mock_plan,
        mock.patch("agent.repo_ask_chat.rag_index_exists") as mock_rag,
    ):
        list(
            chat_ask_generator(
                "explain the facade pattern",
                history,
                state,
                "",
                max_files=5,
            )
        )
    mock_plan.assert_not_called()
    mock_rag.assert_not_called()


def test_ask_list_comprehension_skips_rag_and_planner():
    history = []
    state = {}
    with (
        mock.patch(
            "agent.repo_ask_chat.ask_generate",
            return_value="A list comprehension builds a list from an iterable expression.",
        ),
        mock.patch("agent.repo_ask_chat.plan_ask_query") as mock_plan,
        mock.patch("agent.repo_ask_chat.rag_index_exists") as mock_rag,
    ):
        list(
            chat_ask_generator(
                "what is a list comprehension",
                history,
                state,
                "",
                max_files=5,
            )
        )
    mock_plan.assert_not_called()
    mock_rag.assert_not_called()


def test_ask_pattern_repo_scoped_still_requires_root():
    history = []
    state = {}
    updates = list(
        chat_ask_generator(
            "explain singleton in this repo",
            history,
            state,
            "",
            max_files=5,
        )
    )
    assert "Project root" in updates[-1]["history"][-1]["content"]


def test_ask_generate_pattern_still_code_gen():
    history = []
    state = {}
    with (
        mock.patch(
            "agent.repo_ask_chat.codegen_generate",
            return_value="public class Singleton {}",
        ),
        mock.patch("agent.repo_ask_chat.ask_generate") as mock_ask,
    ):
        updates = list(
            chat_ask_generator(
                "generate singleton pattern",
                history,
                state,
                "",
                max_files=5,
            )
        )
    mock_ask.assert_not_called()
    final = updates[-1]["history"][-1]["content"]
    assert "```" in final
    assert "Project root" not in final


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
    with mock.patch("agent.repo_ask_chat.ask_generate", return_value="Loader class."):
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
    with mock.patch("agent.repo_ask_chat.ask_generate", return_value="This is Main."):
        updates = list(
            chat_ask_generator("explain Main", history, state, str(tmp_path), max_files=5)
        )
    assert updates[-1]["session_state"]["state"] == "qa"
    assert "Main" in updates[-1]["history"][-1]["content"]


def test_ask_follow_up_with_active_file(tmp_path):
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
    with mock.patch("agent.repo_ask_chat.ask_generate", return_value="Follow up answer."):
        updates = list(
            chat_ask_generator("what methods in Main.java?", history, state, str(tmp_path), max_files=5)
        )
    assert "Follow up" in updates[-1]["history"][-1]["content"]


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
    with mock.patch("agent.repo_ask_chat.ask_generate", return_value="Follow up answer."):
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

    per_file_plan = _mock_plan(mode=ANSWER_MODE_PER_FILE, intent="explain selected files")

    with mock.patch("agent.repo_ask_chat.plan_ask_query", return_value=per_file_plan), mock.patch(
        "agent.repo_ask_chat.ask_generate", side_effect=fake_generate
    ):
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
    assert "Explain what `A.java` does" in prompts[0]
    assert "Explain what `B.java` does" in prompts[1]
    final = updates[-1]["history"][-1]["content"]
    assert "**Selected files (2):**" in final
    assert "### A.java" in final
    assert "### B.java" in final


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

    per_file_plan = _mock_plan(mode=ANSWER_MODE_PER_FILE, intent="explain selected files")

    with mock.patch("agent.repo_ask_chat.plan_ask_query", return_value=per_file_plan), mock.patch(
        "agent.repo_ask_chat.ask_generate", side_effect=fake_generate
    ):
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


def test_ask_convert_selected_stays_explain(tmp_path):
    (tmp_path / "A.java").write_text("public class A {}", encoding="utf-8")
    (tmp_path / "B.java").write_text("public class B {}", encoding="utf-8")
    history = []
    state = {"active_files": ["A.java", "B.java"]}
    with mock.patch("agent.repo_ask_chat.ask_generate", return_value="Class A docs."):
        updates = list(
            chat_ask_generator(
                "convert the selected files",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )
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


def test_ask_rag_uses_unified_answer_and_rag_top_k(tmp_path):
    (tmp_path / "A.java").write_text("public class A {}", encoding="utf-8")
    history = []
    state = {}
    prompts: list[str] = []

    chunks = [
        {
            "content": "public class A {}",
            "metadata": {"file_path": "A.java", "type": "class", "name": "A"},
            "score": 0.8,
        },
        {
            "content": "public class B {}",
            "metadata": {"file_path": "B.java", "type": "class", "name": "B"},
            "score": 0.7,
        },
    ]

    def fake_generate(prompt, **kwargs):
        prompts.append(prompt)
        return "Unified repo summary."

    with mock.patch("agent.repo_ask_chat.rag_index_exists", return_value=True), mock.patch(
        "agent.repo_ask_chat.get_repo_rag_pipeline"
    ) as mock_pipeline, mock.patch(
        "agent.repo_ask_chat.plan_ask_query",
        return_value=_mock_plan(
            intent="summarize the overview of this repository",
            retrieval="repository overview architecture main components",
        ),
    ), mock.patch("agent.repo_ask_chat.ask_generate", side_effect=fake_generate):
        _mock_rag_chunks(mock_pipeline, chunks)
        updates = list(
            chat_ask_generator(
                "summarize the overview of this repository",
                history,
                state,
                str(tmp_path),
                max_files=5,
                rag_top_k=7,
            )
        )

    mock_pipeline.return_value.retrieve_overview.assert_called_once()
    assert mock_pipeline.return_value.retrieve_overview.call_args.kwargs["top_k"] == 7
    assert len(prompts) == 1
    assert "A.java" in prompts[0]
    assert "B.java" in prompts[0]
    assert "What the user is asking:" in prompts[0]
    final = updates[-1]["history"][-1]["content"]
    assert "**Retrieved context (2 chunks" in final
    assert "A.java" in final
    assert "class `A`" in final or "· score" in final
    assert "Unified repo summary." in final
    assert updates[-1]["session_state"]["sources_from_rag"] is True


def test_ask_rag_re_retrieves_on_follow_up(tmp_path):
    (tmp_path / "Main.java").write_text("public class Main {}", encoding="utf-8")
    (tmp_path / "Other.java").write_text("public class Other {}", encoding="utf-8")
    history = [
        {"role": "user", "content": "explain key concepts"},
        {"role": "assistant", "content": "Concepts answer."},
    ]
    state = {
        "state": "qa",
        "repo_root": str(tmp_path),
        "sources_cache": [
            {"name": "Main.java", "language": "java", "snippet": "class Main", "ast_summary": ""},
        ],
        "sources_from_rag": True,
    }

    chunks = [
        {
            "content": "public class Other {}",
            "metadata": {"file_path": "Other.java", "type": "class", "name": "Other"},
            "score": 0.75,
        },
    ]

    with mock.patch("agent.repo_ask_chat.rag_index_exists", return_value=True), mock.patch(
        "agent.repo_ask_chat.get_repo_rag_pipeline"
    ) as mock_pipeline, mock.patch(
        "agent.repo_ask_chat.ask_generate", return_value="Component answer."
    ):
        _mock_rag_chunks(mock_pipeline, chunks)
        updates = list(
            chat_ask_generator(
                "what is the key component of this repo?",
                history,
                state,
                str(tmp_path),
                max_files=5,
                rag_top_k=3,
            )
        )

    mock_pipeline.return_value.retrieve.assert_called_once()
    final = updates[-1]["history"][-1]["content"]
    assert "Component answer." in final
    assert "Other.java" in updates[-1]["session_state"]["sources_cache"][0]["name"]


def test_ask_prompt_includes_chat_history(tmp_path):
    (tmp_path / "Main.java").write_text("public class Main {}", encoding="utf-8")
    history = [
        {"role": "user", "content": "explain key concepts"},
        {"role": "assistant", "content": "The repo uses ObjectStore and Blob."},
    ]
    state = {}
    prompts: list[str] = []

    def fake_generate(prompt, **kwargs):
        prompts.append(prompt)
        return "Follow-up with history."

    chunks = [
        {
            "content": "class Main {}",
            "metadata": {"file_path": "Main.java", "type": "class", "name": "Main"},
            "score": 0.9,
        },
    ]

    with mock.patch("agent.repo_ask_chat.rag_index_exists", return_value=True), mock.patch(
        "agent.repo_ask_chat.get_repo_rag_pipeline"
    ) as mock_pipeline, mock.patch("agent.repo_ask_chat.ask_generate", side_effect=fake_generate):
        _mock_rag_chunks(mock_pipeline, chunks)
        list(
            chat_ask_generator(
                "what does Main do?",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )

    assert len(prompts) == 1
    assert "Recent conversation:" in prompts[0]
    assert "explain key concepts" in prompts[0]
    assert "ObjectStore and Blob" in prompts[0]


def test_ask_repo_inventory_includes_full_file_list(tmp_path):
    (tmp_path / "A.java").write_text("public class A {}", encoding="utf-8")
    (tmp_path / "B.java").write_text("public class B {}", encoding="utf-8")
    (tmp_path / "C.java").write_text("public class C {}", encoding="utf-8")
    history = []
    state = {}
    prompts: list[str] = []

    chunks = [
        {
            "content": "public class A {}",
            "metadata": {"file_path": "A.java", "type": "class", "name": "A"},
            "score": 0.85,
        },
    ]

    inventory_plan = _mock_plan(
        mode=ANSWER_MODE_INVENTORY,
        intent="what else does this repo have",
        inventory=True,
    )

    def fake_generate(prompt, **kwargs):
        prompts.append(prompt)
        return "The repo also has B and C."

    with mock.patch("agent.repo_ask_chat.plan_ask_query", return_value=inventory_plan), mock.patch(
        "agent.repo_ask_chat.rag_index_exists", return_value=True
    ), mock.patch("agent.repo_ask_chat.get_repo_rag_pipeline") as mock_pipeline, mock.patch(
        "agent.repo_ask_chat.ask_generate", side_effect=fake_generate
    ):
        _mock_rag_chunks(mock_pipeline, chunks)
        updates = list(
            chat_ask_generator(
                "what else does this repo have?",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )

    assert len(prompts) == 1
    assert "Full repo inventory" in prompts[0]
    assert "B.java" in prompts[0]
    assert "C.java" in prompts[0]
    final = updates[-1]["history"][-1]["content"]
    assert "**Repo inventory (3 files):**" in final
    assert "B.java" in final


def test_ask_repo_overview_without_rag_scans_files(tmp_path):
    (tmp_path / "Main.java").write_text("public class Main {}", encoding="utf-8")
    history = []
    state = {}

    with mock.patch("agent.repo_ask_chat.rag_index_exists", return_value=False), mock.patch(
        "agent.repo_ask_chat.ask_generate", return_value="Project overview."
    ):
        updates = list(
            chat_ask_generator(
                "give me an overview of the project",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )

    final = updates[-1]["history"][-1]["content"]
    assert "Project overview." in final
    assert updates[-1]["session_state"].get("sources_from_rag") is False


@pytest.mark.parametrize(
    "question",
    [
        "what features are missing in the repo?",
        "what's not implemented yet?",
        "compared to real git what does this lack?",
    ],
)
def test_ask_gap_analysis_uses_unified_answer(tmp_path, question):
    for name in ("InitCommand.java", "Commit.java", "StatusCommand.java"):
        (tmp_path / name).write_text(f"public class {name[:-5]} {{}}", encoding="utf-8")
    history = []
    state = {}
    prompts: list[str] = []

    def fake_generate(prompt, **kwargs):
        prompts.append(prompt)
        return "Gap analysis answer."

    with mock.patch("agent.repo_ask_chat.rag_index_exists", return_value=False), mock.patch(
        "agent.repo_ask_chat.ask_generate", side_effect=fake_generate
    ):
        updates = list(
            chat_ask_generator(question, history, state, str(tmp_path), max_files=5)
        )

    assert len(prompts) == 1
    assert "### A.java" not in updates[-1]["history"][-1]["content"]
    assert "Gap analysis answer." in updates[-1]["history"][-1]["content"]


def test_ask_clarification_reuses_cached_sources(tmp_path):
    (tmp_path / "Main.java").write_text("public class Main {}", encoding="utf-8")
    history = [
        {"role": "user", "content": "summarize the repo"},
        {"role": "assistant", "content": "It is a mini-git implementation."},
    ]
    state = {
        "state": "qa",
        "repo_root": str(tmp_path),
        "sources_cache": [
            {"name": "Main.java", "language": "java", "snippet": "class Main", "ast_summary": ""},
        ],
        "sources_from_rag": True,
    }
    prompts: list[str] = []

    clarify_plan = _mock_plan(
        mode=ANSWER_MODE_CLARIFY,
        intent="Restate the previous answer more simply",
        follow_up=True,
    )

    def fake_generate(prompt, **kwargs):
        prompts.append(prompt)
        return "Simple restatement."

    with mock.patch("agent.repo_ask_chat.plan_ask_query", return_value=clarify_plan), mock.patch(
        "agent.repo_ask_chat.ask_generate", side_effect=fake_generate
    ):
        updates = list(
            chat_ask_generator(
                "I didn't get you",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )

    assert len(prompts) == 1
    assert "did not understand" in prompts[0].lower() or "Restate" in prompts[0]
    assert "Simple restatement." in updates[-1]["history"][-1]["content"]
    assert "### Main.java" not in updates[-1]["history"][-1]["content"]


def test_ask_rag_empty_returns_helpful_message(tmp_path):
    history = []
    state = {}

    with mock.patch("agent.repo_ask_chat.rag_index_exists", return_value=True), mock.patch(
        "agent.repo_ask_chat.get_repo_rag_pipeline"
    ) as mock_pipeline:
        _mock_rag_chunks(mock_pipeline, [])
        updates = list(
            chat_ask_generator(
                "explain quantum flux capacitor module",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )

    final = updates[-1]["history"][-1]["content"]
    assert "couldn't find relevant" in final.lower()


def test_sanitize_ask_response_strips_prompt_echo():
    raw = (
        "### Documentation:\n"
        "This script creates a new repository.\n\n"
        "This script creates a new repository."
    )
    cleaned = _sanitize_ask_response(raw)
    assert "### Documentation:" not in cleaned
    assert cleaned.count("This script creates") == 1


def test_sanitize_ask_response_truncates_human_ai_continuation():
    raw = (
        "The file loads a MiniGit repository from disk.\n\n"
        "Human: Can you provide more details on how MiniGit works?\n"
        "AI: Sure! MiniGit is a lightweight Git implementation for IoT."
    )
    cleaned = _sanitize_ask_response(raw)
    assert "loads a MiniGit repository" in cleaned
    assert "Human:" not in cleaned
    assert "IoT" not in cleaned


def test_sanitize_ask_response_truncates_glued_human_marker():
    raw = (
        "This setup allows developers to manage MiniGit repositories within their "
        "applications.Human: Can you provide more details?"
    )
    cleaned = _sanitize_ask_response(raw)
    assert cleaned.endswith("applications.")
    assert "Human:" not in cleaned


def test_ask_single_selected_file_uses_file_prompt(tmp_path):
    rel = "mini-git/src/main/java/com/example/RepositoryLoader.java"
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("public class RepositoryLoader {}", encoding="utf-8")
    history = []
    state = {"active_files": [rel]}
    prompts: list[str] = []

    def fake_generate(prompt, **kwargs):
        prompts.append(prompt)
        return "RepositoryLoader loads the repo from disk."

    with mock.patch("agent.repo_ask_chat.ask_generate", side_effect=fake_generate):
        updates = list(
            chat_ask_generator(
                "what is there in the selected file?",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )

    assert len(prompts) == 1
    assert "Answer the developer's question about this source file." in prompts[0]
    assert "Recent conversation:" not in prompts[0]
    assert "RepositoryLoader.java" in prompts[0]
    final = updates[-1]["history"][-1]["content"]
    assert "**Selected files (1):**" in final
    assert "RepositoryLoader loads the repo" in final


def test_sanitize_rejects_trivial_yes():
    cleaned = _sanitize_ask_response("Yes")
    assert "couldn't generate a reliable answer" in cleaned.lower()


def test_apply_plan_heuristics_overview_question():
    plan = apply_plan_heuristics(
        _mock_plan(intent="user wants summary", retrieval="key points"),
        "can you summarise key points in the repo",
    )
    assert plan.answer_mode == ANSWER_MODE_DIRECT
    assert plan.retrieval_query == OVERVIEW_RETRIEVAL_QUERY


def test_apply_plan_heuristics_overview_of_named_file_keeps_query():
    """An overview of one file must not be widened into a repo overview."""
    question = "give me overview of readme.md file"
    plan = apply_plan_heuristics(
        _mock_plan(intent="user wants the readme", retrieval="repo"), question
    )
    assert plan.answer_mode == ANSWER_MODE_DIRECT
    assert plan.retrieval_query == question


def test_retrieve_sources_scopes_to_named_doc_file(tmp_path):
    mock_pipeline = mock.Mock()
    mock_pipeline.resolve_index_paths.return_value = ["mini-git/README.md"]
    mock_pipeline.retrieve_overview.return_value = [
        {
            "content": "# MiniGit",
            "metadata": {
                "file_path": "mini-git/README.md",
                "type": "doc",
                "name": "MiniGit",
            },
            "score": 0.81,
        }
    ]

    with mock.patch("agent.repo_ask_chat.rag_index_exists", return_value=True), mock.patch(
        "agent.repo_ask_chat.get_repo_rag_pipeline", return_value=mock_pipeline
    ):
        sources, files, from_rag, err = _retrieve_sources(
            str(tmp_path),
            "give me overview of readme.md file",
            max_files=5,
            rag_top_k=5,
            overview=True,
            file_refs=["readme.md"],
        )

    assert err is None
    assert from_rag is True
    assert files == ["mini-git/README.md"]
    assert sources[0]["language"] == "markdown"
    kwargs = mock_pipeline.retrieve_overview.call_args.kwargs
    assert kwargs["file_paths"] == ["mini-git/README.md"]
    assert kwargs["score_margin"] is not None
    assert kwargs["path_boost"] is True
    # A file-scoped question must not fall back to the generic repo overview.
    assert mock_pipeline.retrieve_overview.call_count == 1


def test_retrieve_sources_skips_retry_for_generic_overview_query(tmp_path):
    mock_pipeline = mock.Mock()
    weak_chunk = [
        {
            "content": "class Command",
            "metadata": {"file_path": "Command.py", "type": "class", "name": "Command"},
            "score": 0.40,
        }
    ]
    mock_pipeline.retrieve_overview.return_value = weak_chunk

    with mock.patch("agent.repo_ask_chat.rag_index_exists", return_value=True), mock.patch(
        "agent.repo_ask_chat.get_repo_rag_pipeline", return_value=mock_pipeline
    ):
        _retrieve_sources(
            str(tmp_path),
            OVERVIEW_RETRIEVAL_QUERY,
            max_files=5,
            rag_top_k=5,
            overview=True,
        )

    # Re-running the identical query would only waste a second encode.
    assert mock_pipeline.retrieve_overview.call_count == 1


def test_retrieve_sources_does_not_scope_without_refs(tmp_path):
    mock_pipeline = mock.Mock()
    mock_pipeline.retrieve.return_value = [
        {
            "content": "class Commit",
            "metadata": {"file_path": "Commit.java", "type": "class", "name": "Commit"},
            "score": 0.80,
        }
    ]

    with mock.patch("agent.repo_ask_chat.rag_index_exists", return_value=True), mock.patch(
        "agent.repo_ask_chat.get_repo_rag_pipeline", return_value=mock_pipeline
    ):
        _retrieve_sources(
            str(tmp_path), "how does commit work", max_files=5, rag_top_k=5
        )

    mock_pipeline.resolve_index_paths.assert_not_called()
    assert mock_pipeline.retrieve.call_args.kwargs["file_paths"] is None


def test_retrieve_sources_retries_on_weak_scores(tmp_path):
    mock_pipeline = mock.Mock()
    weak_chunk = [
        {
            "content": "class Command",
            "metadata": {"file_path": "Command.py", "type": "class", "name": "Command"},
            "score": 0.42,
        }
    ]
    strong_chunk = [
        {
            "content": "# MiniGit",
            "metadata": {"file_path": "README.md", "type": "doc", "name": "README.md"},
            "score": 0.71,
        }
    ]
    mock_pipeline.retrieve_overview.side_effect = [weak_chunk, strong_chunk]

    with mock.patch("agent.repo_ask_chat.rag_index_exists", return_value=True), mock.patch(
        "agent.repo_ask_chat.get_repo_rag_pipeline", return_value=mock_pipeline
    ):
        sources, files, from_rag, err = _retrieve_sources(
            str(tmp_path),
            "summarise key points",
            max_files=5,
            rag_top_k=8,
            overview=True,
        )

    assert err is None
    assert from_rag is True
    assert files == ["README.md"]
    assert mock_pipeline.retrieve_overview.call_count == 2


def test_retrieve_sources_rejects_persistent_weak_scores(tmp_path):
    mock_pipeline = mock.Mock()
    weak_chunk = [
        {
            "content": "class Command",
            "metadata": {"file_path": "Command.py", "type": "class", "name": "Command"},
            "score": 0.41,
        }
    ]
    mock_pipeline.retrieve_overview.side_effect = [weak_chunk, weak_chunk]

    with mock.patch("agent.repo_ask_chat.rag_index_exists", return_value=True), mock.patch(
        "agent.repo_ask_chat.get_repo_rag_pipeline", return_value=mock_pipeline
    ):
        sources, files, from_rag, err = _retrieve_sources(
            str(tmp_path),
            "summarise key points",
            max_files=5,
            rag_top_k=8,
            overview=True,
        )

    assert sources == []
    assert files == []
    assert err is not None
    assert "confident matches" in err.lower()


def test_ask_overview_question_uses_overview_retrieval(tmp_path):
    (tmp_path / "Main.java").write_text("public class Main {}", encoding="utf-8")
    history = []
    state = {}

    mock_pipeline = mock.Mock()
    mock_pipeline.retrieve_overview.return_value = [
        {
            "content": "# Overview",
            "metadata": {"file_path": "README.md", "type": "doc", "name": "README.md"},
            "score": 0.8,
        }
    ]
    mock_pipeline.retrieve.return_value = mock_pipeline.retrieve_overview.return_value

    overview_plan = _mock_plan(
        intent="summarise key points",
        retrieval=OVERVIEW_RETRIEVAL_QUERY,
    )

    with mock.patch("agent.repo_ask_chat.plan_ask_query", return_value=overview_plan), mock.patch(
        "agent.repo_ask_chat.rag_index_exists", return_value=True
    ), mock.patch(
        "agent.repo_ask_chat.get_repo_rag_pipeline", return_value=mock_pipeline
    ), mock.patch(
        "agent.repo_ask_chat.ask_generate",
        return_value="MiniGit implements git init, add, commit, and log commands.",
    ):
        updates = list(
            chat_ask_generator(
                "can you summarise key points in the repo",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )

    mock_pipeline.retrieve_overview.assert_called()
    final = updates[-1]["history"][-1]["content"]
    assert "MiniGit implements git init" in final
    assert updates[-1]["session_state"]["ask_plan"]["retrieval_query"] == OVERVIEW_RETRIEVAL_QUERY


def test_plan_ask_query_fallback_without_llm():
    from agent.ask_query_planner import plan_ask_query

    plan = plan_ask_query("what is missing?", [], use_llm=False)
    assert plan.answer_mode == ANSWER_MODE_DIRECT
    assert plan.retrieval_query


def test_apply_plan_heuristics_architecture_question():
    from agent.ask_query_planner import apply_plan_heuristics

    plan = apply_plan_heuristics(
        _mock_plan(mode=ANSWER_MODE_INVENTORY, inventory=True),
        "explain how mini git works in this repo",
    )
    assert plan.answer_mode == ANSWER_MODE_DIRECT
    assert plan.needs_repo_inventory is False


def test_apply_plan_heuristics_misclassified_inventory():
    from agent.ask_query_planner import apply_plan_heuristics

    plan = apply_plan_heuristics(
        _mock_plan(mode=ANSWER_MODE_INVENTORY, inventory=True),
        "summarize the main workflow",
    )
    assert plan.answer_mode == ANSWER_MODE_DIRECT
    assert plan.needs_repo_inventory is False


def test_apply_plan_heuristics_keeps_explicit_inventory():
    from agent.ask_query_planner import apply_plan_heuristics

    plan = apply_plan_heuristics(
        _mock_plan(mode=ANSWER_MODE_INVENTORY, inventory=True),
        "what else does this repo have?",
    )
    assert plan.answer_mode == ANSWER_MODE_INVENTORY
    assert plan.needs_repo_inventory is True


def test_ask_follow_up_with_sticky_active_files_uses_picker_selection(tmp_path):
    for name in ("InitCommand.java", "CommitCommand.java", "ObjectStore.java"):
        (tmp_path / name).write_text(f"public class {name[:-5]} {{}}", encoding="utf-8")
    history = [
        {"role": "user", "content": "summarize key concepts"},
        {"role": "assistant", "content": "Key concepts answer."},
    ]
    state = {
        "state": "qa",
        "repo_root": str(tmp_path),
        "active_files": ["InitCommand.java", "CommitCommand.java"],
        "sources_cache": [
            {
                "name": "InitCommand.java",
                "language": "java",
                "snippet": "class InitCommand",
                "ast_summary": "",
            },
        ],
        "sources_from_rag": True,
    }

    with mock.patch("agent.repo_ask_chat.rag_index_exists", return_value=True), mock.patch(
        "agent.repo_ask_chat.get_repo_rag_pipeline"
    ) as mock_pipeline, mock.patch(
        "agent.repo_ask_chat.ask_generate", return_value="Init and commit commands."
    ):
        updates = list(
            chat_ask_generator(
                "explain how mini git works",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )

    mock_pipeline.return_value.retrieve.assert_not_called()
    mock_pipeline.return_value.retrieve_overview.assert_not_called()
    final = updates[-1]["history"][-1]["content"]
    assert "**Selected files (2):**" in final
    assert "InitCommand.java" in final
    assert "CommitCommand.java" in final
    assert "Init and commit commands." in final
    assert updates[-1]["session_state"].get("sources_from_rag") is False


def test_ask_picker_single_file_scopes_to_file(tmp_path):
    (tmp_path / "Main.java").write_text("public class Main {}", encoding="utf-8")
    (tmp_path / "Other.java").write_text("public class Other {}", encoding="utf-8")
    history = []
    state = {"active_files": ["Main.java"]}

    with mock.patch("agent.repo_ask_chat.ask_generate", return_value="Main class answer."), mock.patch(
        "agent.repo_ask_chat.rag_index_exists", return_value=True
    ), mock.patch("agent.repo_ask_chat.get_repo_rag_pipeline") as mock_pipeline:
        updates = list(
            chat_ask_generator(
                "explain the main logic",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )

    mock_pipeline.return_value.retrieve.assert_not_called()
    assert len(updates[-1]["session_state"]["sources_cache"]) == 1
    assert updates[-1]["session_state"]["sources_cache"][0]["name"] == "Main.java"
    assert updates[-1]["session_state"]["sources_from_rag"] is False
    final = updates[-1]["history"][-1]["content"]
    assert "**Selected files (1):**" in final
    assert "Main class answer." in final


def test_ask_at_file_in_message_scopes_to_file(tmp_path):
    (tmp_path / "Foo.java").write_text("public class Foo {}", encoding="utf-8")
    (tmp_path / "Bar.java").write_text("public class Bar {}", encoding="utf-8")
    history = []
    state = {}

    with mock.patch("agent.repo_ask_chat.ask_generate", return_value="Foo class answer."), mock.patch(
        "agent.repo_ask_chat.rag_index_exists", return_value=True
    ), mock.patch("agent.repo_ask_chat.get_repo_rag_pipeline") as mock_pipeline:
        updates = list(
            chat_ask_generator(
                "explain @Foo.java",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )

    mock_pipeline.return_value.retrieve.assert_not_called()
    assert len(updates[-1]["session_state"]["sources_cache"]) == 1
    assert "Foo.java" in updates[-1]["session_state"]["sources_cache"][0]["name"]
    final = updates[-1]["history"][-1]["content"]
    assert "**Selected files (1):**" in final
    assert "Foo class answer." in final


def test_ask_architecture_question_no_inventory_with_misclassified_plan(tmp_path):
    (tmp_path / "Repository.java").write_text("public class Repository {}", encoding="utf-8")
    (tmp_path / "Commit.java").write_text("public class Commit {}", encoding="utf-8")
    history = []
    state = {}
    prompts: list[str] = []

    inventory_plan = _mock_plan(
        mode=ANSWER_MODE_INVENTORY,
        intent="explain how mini git works",
        inventory=True,
    )

    chunks = [
        {
            "content": "public class Repository {}",
            "metadata": {"file_path": "Repository.java", "type": "class", "name": "Repository"},
            "score": 0.88,
        },
        {
            "content": "public class Commit {}",
            "metadata": {"file_path": "Commit.java", "type": "class", "name": "Commit"},
            "score": 0.84,
        },
    ]

    def fake_generate(prompt, **kwargs):
        prompts.append(prompt)
        return "MiniGit uses Repository to manage commits and refs."

    with mock.patch("agent.repo_ask_chat.plan_ask_query", return_value=inventory_plan), mock.patch(
        "agent.repo_ask_chat.rag_index_exists", return_value=True
    ), mock.patch("agent.repo_ask_chat.get_repo_rag_pipeline") as mock_pipeline, mock.patch(
        "agent.repo_ask_chat.ask_generate", side_effect=fake_generate
    ):
        _mock_rag_chunks(mock_pipeline, chunks)
        updates = list(
            chat_ask_generator(
                "explain how mini git works",
                history,
                state,
                str(tmp_path),
                max_files=5,
            )
        )

    assert len(prompts) == 1
    assert "Full repo inventory" not in prompts[0]
    final = updates[-1]["history"][-1]["content"]
    assert "**Repo inventory" not in final
    assert "MiniGit uses Repository to manage commits and refs." in final
