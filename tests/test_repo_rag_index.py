"""Tests for repository RAG index path helpers."""

from inference.repo_rag_pipeline import (
    legacy_repo_index_dir,
    repo_index_dir,
    repo_index_key,
)


def test_repo_index_key_is_stable_and_unique(tmp_path):
    a = tmp_path / "proj_a"
    b = tmp_path / "proj_b"
    a.mkdir()
    b.mkdir()
    assert repo_index_key(str(a)) == repo_index_key(str(a))
    assert repo_index_key(str(a)) != repo_index_key(str(b))
    assert repo_index_dir(str(a)).name != legacy_repo_index_dir(str(a)).name
