"""Tests for repository index building."""

from unittest import mock

from agent.chunking import chunk_markdown_doc
from scripts.build_repo_index import build_index_for_repo


def _capture_chunks(repo_root: str) -> list[dict]:
    captured: list[list[dict]] = []
    with mock.patch("scripts.build_repo_index.RepoRAGPipeline") as mock_pipeline:
        mock_pipeline.return_value.build_index.side_effect = captured.append
        build_index_for_repo(repo_root)
    return captured[0] if captured else []


def test_chunk_markdown_doc_splits_on_headings():
    content = (
        "Intro line.\n\n"
        "# Title\n\n"
        + "Body of title. " * 60
        + "\n\n## Section Two\n\n"
        + "Body of section two. " * 60
        + "\n\n### Nested\n\nstays with parent\n"
    )
    chunks = chunk_markdown_doc("docs/README.md", content)

    names = [chunk["metadata"]["name"] for chunk in chunks]
    assert "Section Two" in names
    assert all(chunk["metadata"]["type"] == "doc" for chunk in chunks)
    assert all(chunk["metadata"]["file_path"] == "docs/README.md" for chunk in chunks)
    # Level-3 headings are not split out on their own.
    assert "Nested" not in names
    section = next(c for c in chunks if c["metadata"]["name"] == "Section Two")
    assert "stays with parent" in section["content"]


def test_chunk_markdown_doc_merges_short_boilerplate():
    content = (
        "# Overview\n\n"
        + "Substantial overview prose. " * 40
        + "\n\n## License\n\nMIT\n\n## Contributing\n\nPRs welcome\n"
    )
    chunks = chunk_markdown_doc("README.md", content)

    names = [chunk["metadata"]["name"] for chunk in chunks]
    assert names == ["Overview"]
    assert "MIT" in chunks[0]["content"]
    assert "PRs welcome" in chunks[0]["content"]
    assert chunks[0]["metadata"]["end_line"] == len(content.splitlines())


def test_chunk_markdown_doc_handles_empty_and_headingless():
    assert chunk_markdown_doc("a.md", "   \n") == []
    plain = chunk_markdown_doc("a.md", "just some text")
    assert len(plain) == 1
    assert plain[0]["metadata"]["name"] == "a.md"


def test_build_index_chunks_all_docs_not_only_readme(tmp_path):
    (tmp_path / "README.md").write_text(
        "# Readme\n\n" + "readme body " * 60, encoding="utf-8"
    )
    (tmp_path / "ROADMAP.md").write_text(
        "# Roadmap\n\n" + "roadmap body " * 60, encoding="utf-8"
    )

    chunks = _capture_chunks(str(tmp_path))
    doc_paths = {
        chunk["metadata"]["file_path"]
        for chunk in chunks
        if chunk["metadata"]["type"] == "doc"
    }
    assert doc_paths == {"README.md", "ROADMAP.md"}


def test_build_index_skips_py_when_java_exists(tmp_path):
    (tmp_path / "Foo.java").write_text("public class Foo {}", encoding="utf-8")
    (tmp_path / "Foo.py").write_text("class Foo: pass", encoding="utf-8")
    (tmp_path / "Bar.py").write_text("class Bar: pass", encoding="utf-8")

    captured: list[list[dict]] = []

    def fake_build_index(chunks):
        captured.append(chunks)

    with mock.patch("scripts.build_repo_index.RepoRAGPipeline") as mock_pipeline:
        mock_pipeline.return_value.build_index.side_effect = fake_build_index
        build_index_for_repo(str(tmp_path))

    assert captured
    paths = [chunk["metadata"]["file_path"] for chunk in captured[0]]
    assert any(path.endswith("Foo.java") for path in paths)
    assert not any(path.endswith("Foo.py") for path in paths)
    assert any(path.endswith("Bar.py") for path in paths)
