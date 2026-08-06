"""Tests for repo workspace utilities."""

from pathlib import Path
from unittest import mock

from agent.repo_utils import (
    AmbiguousFileMatch,
    apply_pending_writes,
    detect_ask_task,
    detect_code_task,
    discard_pending_writes,
    empty_session,
    extract_file_refs,
    filter_sources_for_question,
    format_active_files_html,
    format_sources_block,
    index_repo_files,
    list_repo_relative_files,
    pending_to_review_data,
    queue_write,
    resolve_active_file_queries,
    resolve_file_query,
    resolve_in_repo,
    search_repo_files,
    set_active_files,
    to_relative_repo_path,
    trim_sources_for_prompt,
)


def test_empty_session():
    s = empty_session("/tmp/repo")
    assert s["repo_root"] == "/tmp/repo"
    assert s["pending_writes"] == []
    assert s["active_files"] == []


def test_queue_and_discard():
    s = empty_session()
    queue_write(s, "/tmp/a.py", "x = 1", name="a.py", python="x = 1")
    assert len(s["pending_writes"]) == 1
    assert discard_pending_writes(s) == 1
    assert s["pending_writes"] == []


def test_apply_pending_writes(tmp_path):
    s = empty_session(str(tmp_path))
    target = tmp_path / "out.py"
    queue_write(s, str(target), "print(1)", python="print(1)")

    writes = []

    def fake_write(args):
        writes.append((args["path"], args["content"]))
        return "ok"

    mock_tool = mock.MagicMock()
    mock_tool.invoke = fake_write
    with mock.patch("agent.repo_utils.write_text_file", mock_tool):
        applied = apply_pending_writes(s)
    assert applied == [str(target)]
    assert writes[0][1] == "print(1)"


def test_resolve_in_repo(tmp_path):
    sub = tmp_path / "src"
    sub.mkdir()
    p = resolve_in_repo(str(tmp_path), "src")
    assert p == sub.resolve()


def test_index_repo_files(tmp_path):
    (tmp_path / "A.java").write_text("class A {}", encoding="utf-8")
    (tmp_path / "b.py").write_text("x=1", encoding="utf-8")
    files = index_repo_files(str(tmp_path), max_files=10)
    assert len(files) == 2


def test_pending_to_review_data():
    s = empty_session()
    queue_write(s, "/x/App.py", "class App: pass", java="class App {}", python="class App: pass")
    data = pending_to_review_data(s)
    assert data[0]["name"] == "App.py"
    assert "class App" in data[0]["python"]


def test_extract_file_refs():
    refs = extract_file_refs("explain @Repository.java and App.py")
    assert "Repository.java" in refs
    assert "App.py" in refs


def test_filter_sources_for_question():
    sources = [
        {"name": "core/Repository.java", "snippet": "class R", "language": "java"},
        {"name": "core/App.java", "snippet": "class A", "language": "java"},
    ]
    filtered = filter_sources_for_question(sources, "explain Repository.java")
    assert len(filtered) == 1
    assert "Repository" in filtered[0]["name"]


def test_list_repo_relative_files(tmp_path):
    nested = tmp_path / "src" / "main"
    nested.mkdir(parents=True)
    (nested / "App.java").write_text("class App {}", encoding="utf-8")
    files = list_repo_relative_files(str(tmp_path))
    assert "src/main/App.java" in files


def test_resolve_file_query_nested_basename(tmp_path):
    nested = tmp_path / "src" / "main"
    nested.mkdir(parents=True)
    target = nested / "RepositoryLoader.java"
    target.write_text("class RepositoryLoader {}", encoding="utf-8")
    (tmp_path / "Other.java").write_text("class Other {}", encoding="utf-8")

    resolved = resolve_file_query(str(tmp_path), "RepositoryLoader.java")
    assert resolved == target.resolve()


def test_resolve_file_query_relative_path(tmp_path):
    sub = tmp_path / "src"
    sub.mkdir()
    p = sub / "Main.java"
    p.write_text("class Main {}", encoding="utf-8")
    resolved = resolve_file_query(str(tmp_path), "src/Main.java")
    assert resolved == p.resolve()


def test_resolve_file_query_ambiguous(tmp_path):
    a = tmp_path / "a" / "Utils.java"
    b = tmp_path / "b" / "Utils.java"
    a.parent.mkdir()
    b.parent.mkdir()
    a.write_text("class A {}", encoding="utf-8")
    b.write_text("class B {}", encoding="utf-8")

    try:
        resolve_file_query(str(tmp_path), "Utils.java")
        assert False, "expected AmbiguousFileMatch"
    except AmbiguousFileMatch as exc:
        assert len(exc.candidates) == 2


def test_search_repo_files(tmp_path):
    nested = tmp_path / "src"
    nested.mkdir()
    (nested / "RepositoryLoader.java").write_text("class R {}", encoding="utf-8")
    matches = search_repo_files(str(tmp_path), "Repository")
    assert any("RepositoryLoader.java" in m for m in matches)


def test_to_relative_repo_path(tmp_path):
    nested = tmp_path / "src" / "main"
    nested.mkdir(parents=True)
    target = nested / "App.java"
    target.write_text("class App {}", encoding="utf-8")
    assert to_relative_repo_path(str(tmp_path), str(target)) == "src/main/App.java"
    assert to_relative_repo_path(str(tmp_path), "src/main/App.java") == "src/main/App.java"


def test_set_active_files_deduplicates(tmp_path):
    nested = tmp_path / "src"
    nested.mkdir()
    f = nested / "Main.java"
    f.write_text("class Main {}", encoding="utf-8")
    state = empty_session(str(tmp_path))
    set_active_files(state, str(tmp_path), [str(f), str(f)])
    assert state["active_files"] == ["src/Main.java"]


def test_resolve_active_file_queries_picker_over_message(tmp_path):
    nested = tmp_path / "src"
    nested.mkdir()
    a = nested / "A.java"
    b = nested / "B.java"
    a.write_text("class A {}", encoding="utf-8")
    b.write_text("class B {}", encoding="utf-8")

    paths, err = resolve_active_file_queries(
        str(tmp_path), "explain A.java", ["src/B.java"]
    )
    assert err is None
    assert len(paths) == 1
    assert paths[0].endswith("B.java")


def test_resolve_active_file_queries_session_fallback(tmp_path):
    nested = tmp_path / "src"
    nested.mkdir()
    b = nested / "B.java"
    b.write_text("class B {}", encoding="utf-8")

    paths, err = resolve_active_file_queries(str(tmp_path), "explain this", ["src/B.java"])
    assert err is None
    assert len(paths) == 1
    assert paths[0].endswith("B.java")


def test_resolve_active_file_queries_basename_fallback(tmp_path):
    nested = tmp_path / "src" / "main"
    nested.mkdir(parents=True)
    target = nested / "RepositoryLoader.java"
    target.write_text("class RepositoryLoader {}", encoding="utf-8")

    paths, err = resolve_active_file_queries(
        str(tmp_path), "migrate RepositoryLoader", [], extensions=".java"
    )
    assert err is None
    assert len(paths) == 1
    assert paths[0].endswith("RepositoryLoader.java")


def test_resolve_active_file_queries_ambiguous_basename(tmp_path):
    a = tmp_path / "a" / "Utils.java"
    b = tmp_path / "b" / "Utils.java"
    a.parent.mkdir()
    b.parent.mkdir()
    a.write_text("class A {}", encoding="utf-8")
    b.write_text("class B {}", encoding="utf-8")

    paths, err = resolve_active_file_queries(
        str(tmp_path), "migrate Utils", [], extensions=".java"
    )
    assert paths == []
    assert err is not None
    assert "Multiple files match" in err


def test_format_active_files_html():
    html = format_active_files_html(["src/Main.java", "lib/util.py"])
    assert "file-chip" in html
    assert "src/Main.java" in html
    assert format_active_files_html([]) == ""


def test_format_sources_block_for_doc():
    sources = [
        {
            "name": "App.java",
            "language": "java",
            "snippet": "public class App {}",
            "ast_summary": "java_classes≈['App']",
        }
    ]
    block = format_sources_block(sources, for_doc=True)
    assert "Structure:" not in block
    assert "java_classes" not in block
    assert "App.java" in block


def test_trim_sources_keeps_all_files():
    sources = [
        {"name": f"F{i}.java", "snippet": "x" * 5000, "ast_summary": "s", "language": "java"}
        for i in range(4)
    ]
    trimmed = trim_sources_for_prompt(sources)
    assert len(trimmed) == 4
    block = format_sources_block(trimmed)
    for i in range(4):
        assert f"F{i}.java" in block


def test_detect_code_task_nl_python():
    assert detect_code_task("python: factorial") == "gen_python"
    assert detect_code_task("write python hello") == "gen_python"
    assert detect_code_task("write a login endpoint") == "gen_python"


def test_detect_code_task_nl_java():
    assert detect_code_task("java: REST controller") == "gen_java"
    assert detect_code_task("write java simple class") == "gen_java"


def test_detect_code_task_migrate():
    assert detect_code_task("migrate Main.java") == "migrate"
    assert detect_code_task("src/Main.java") == "migrate"
    assert detect_code_task(
        "convert the selected files", ["A.java", "B.java"]
    ) == "migrate"
    assert detect_code_task("convert", ["Main.java"]) == "migrate"


def test_detect_code_task_nl_python_over_migrate():
    assert detect_code_task("convert string to int in python") == "gen_python"
    assert detect_code_task("convert string to int in python", ["A.java"]) == "gen_python"


def test_detect_ask_task_explain():
    assert detect_ask_task("explain selected files") == "explain"
    assert detect_ask_task("what does Main.java do?") == "explain"
    assert detect_ask_task("migrate Main.java") == "explain"
    assert detect_ask_task("convert the selected files") == "explain"
    assert detect_ask_task("what is this project?") == "explain"
    assert detect_ask_task("how does CommandParser work?") == "explain"
    assert detect_ask_task("tell me about this repo") == "explain"
    assert detect_ask_task("summarize the selected files") == "explain"
    assert detect_ask_task("what does this program do") == "explain"


def test_detect_ask_task_gen_code():
    prompts_python = (
        "python: factorial function",
        "write python hello world",
        "generate python REST client",
        "Give me a program that converts Java to Python",
        "write a program to parse CSV files",
        "Write a parser that reads the excel sheet row by row",
        "implement a login system",
        "create a function to validate email addresses",
        "I need code to read CSV files",
        "can you write a script that downloads images",
        "help me build an API endpoint for users",
        "how to implement binary search in python",
        "show me the code for merge sort",
        "implement factorial",
        "generate fibonacci sequence",
        "coding challenge: two sum problem",
        "write a REST API for todo items",
        "build a websocket server",
        "make a calculator app",
        "develop a scraper for news headlines",
    )
    for prompt in prompts_python:
        assert detect_ask_task(prompt) == "gen_python", prompt

    assert detect_ask_task("java: simple class") == "gen_java"
    assert detect_ask_task("write java controller") == "gen_java"
    assert detect_ask_task("create a java class for users") == "gen_java"
    assert detect_ask_task("implement a servlet in java") == "gen_java"
    assert detect_ask_task("build a spring boot controller in java") == "gen_java"

