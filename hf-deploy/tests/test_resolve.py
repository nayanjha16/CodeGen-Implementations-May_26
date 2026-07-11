"""Tests for best-adapter resolution."""

from __future__ import annotations

from pathlib import Path

import pytest

from hf_deploy.adapters.resolve import resolve_best_adapter, resolve_version_adapters


def _touch_adapter(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "adapter_config.json").write_text("{}", encoding="utf-8")
    (path / "adapter_model.safetensors").write_bytes(b"x")


def test_resolve_prefers_task_root(tmp_path: Path) -> None:
    task = tmp_path / "text2sql"
    _touch_adapter(task)
    _touch_adapter(task / "checkpoint-999")
    assert resolve_best_adapter(task) == task


def test_resolve_falls_back_to_highest_checkpoint(tmp_path: Path) -> None:
    task = tmp_path / "text2sql"
    task.mkdir()
    _touch_adapter(task / "checkpoint-10")
    _touch_adapter(task / "checkpoint-50")
    assert resolve_best_adapter(task) == task / "checkpoint-50"


def test_resolve_version_adapters(tmp_path: Path) -> None:
    version = tmp_path / "v3"
    for task in ("text2sql", "sql2nosql", "nosql2doc"):
        _touch_adapter(version / task)
    resolved = resolve_version_adapters(tmp_path, "v3")
    assert set(resolved) == {"text2sql", "sql2nosql", "nosql2doc"}
    assert all(p.name == intent for intent, p in resolved.items())


def test_resolve_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        resolve_best_adapter(tmp_path / "missing")
