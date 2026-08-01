from pathlib import Path

from src.artifact_manifest import (
    atomic_write_json,
    load_json,
    manifests_compatible,
    repository_manifest,
    repository_tree_hash,
)


def test_repository_hash_changes_with_source(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    source = repo / "module.py"
    source.write_text("def one():\n    return 1\n", encoding="utf-8")
    before = repository_tree_hash(repo)
    source.write_text("def one():\n    return 2\n", encoding="utf-8")
    assert repository_tree_hash(repo) != before


def test_manifest_detects_repository_change(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "A.java").write_text("class A {}", encoding="utf-8")
    first = repository_manifest(repo, "model", 384)
    (repo / "A.java").write_text("class A { int x; }", encoding="utf-8")
    second = repository_manifest(repo, "model", 384)
    assert not manifests_compatible(first, second, ("source_tree_hash",))


def test_atomic_json_round_trip(tmp_path: Path):
    path = tmp_path / "manifest.json"
    atomic_write_json(path, {"version": 3})
    assert load_json(path) == {"version": 3}
