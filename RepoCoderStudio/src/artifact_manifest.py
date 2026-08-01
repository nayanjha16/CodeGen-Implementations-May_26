"""Versioned manifests and fingerprints for repository/corpus retrieval artifacts."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

INDEX_FORMAT_VERSION = "repocoder_index_v4"
PARSER_VERSION = "repo_explorer_v3"
STAGE4_IMPLEMENTATION_PROVENANCE = {
    "status": "reconstructed",
    "basis": "Stage 4 technical documentation",
    "original_source_available": False,
    "claim_boundary": (
        "Functionally tested against the documented interface; not claimed "
        "as a byte-for-byte copy of the original Kaggle-authored source."
    ),
}


def _sha256_chunks(chunks: Iterable[bytes]) -> str:
    digest = hashlib.sha256()
    for chunk in chunks:
        digest.update(chunk)
    return digest.hexdigest()


def file_sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return _sha256_chunks(iter(lambda: handle.read(1024 * 1024), b""))


def repository_tree_hash(repo_path: Path) -> str:
    """Hash supported source paths and bytes deterministically."""
    repo_path = repo_path.resolve()
    paths = sorted(
        p for p in repo_path.rglob("*")
        if p.is_file()
        and not p.is_symlink()
        and p.suffix.lower() in {".py", ".java"}
        and p.stat().st_size <= 2_000_000
        and not any(
            part in {
                ".git", ".hg", ".svn", "__pycache__", ".venv", "venv",
                "node_modules", "build", "dist", "target",
            }
            for part in p.parts
        )
    )
    digest = hashlib.sha256()
    for path in paths:
        rel = path.relative_to(repo_path).as_posix().encode("utf-8")
        digest.update(len(rel).to_bytes(8, "big"))
        digest.update(rel)
        digest.update(file_sha256(path).encode("ascii"))
    return digest.hexdigest()


def git_commit(repo_path: Path) -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def repository_manifest(
    repo_path: Path,
    embedding_model: str,
    embedding_dimension: int,
    component_counts: Optional[Dict[str, int]] = None,
    mock_embeddings: bool = False,
) -> Dict[str, Any]:
    resolved = repo_path.resolve()
    return {
        "format_version": INDEX_FORMAT_VERSION,
        "parser_version": PARSER_VERSION,
        "repository_root": str(resolved),
        "git_commit": git_commit(resolved),
        "source_tree_hash": repository_tree_hash(resolved),
        "embedding_model": embedding_model,
        "embedding_dimension": int(embedding_dimension),
        "mock_embeddings": bool(mock_embeddings),
        "component_counts": component_counts or {},
        "implementation_provenance": STAGE4_IMPLEMENTATION_PROVENANCE,
    }


def corpus_manifest(
    corpus_path: Path,
    embedding_model: str,
    embedding_dimension: int,
    indexed_rows: int,
    mock_embeddings: bool,
) -> Dict[str, Any]:
    return {
        "format_version": INDEX_FORMAT_VERSION,
        "corpus_path": str(corpus_path.resolve()),
        "corpus_sha256": file_sha256(corpus_path),
        "split_filter": "train",
        "embedding_model": embedding_model,
        "embedding_dimension": int(embedding_dimension),
        "mock_embeddings": bool(mock_embeddings),
        "indexed_rows": int(indexed_rows),
    }


def manifests_compatible(expected: Dict[str, Any], actual: Dict[str, Any], keys: Iterable[str]) -> bool:
    return all(expected.get(key) == actual.get(key) for key in keys)


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return None


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        try:
            Path(tmp_name).unlink()
        except FileNotFoundError:
            pass


def promote_directory(staged: Path, destination: Path) -> None:
    """Promote a complete directory with rollback if the final rename fails."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    backup = destination.with_name(destination.name + ".previous")
    if backup.exists():
        shutil.rmtree(backup)
    if destination.exists():
        os.replace(destination, backup)
    try:
        os.replace(staged, destination)
    except Exception:
        if backup.exists() and not destination.exists():
            os.replace(backup, destination)
        raise
    if backup.exists():
        shutil.rmtree(backup)
