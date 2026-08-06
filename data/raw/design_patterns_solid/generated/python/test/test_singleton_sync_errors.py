"""Pytest for singleton_sync_errors (singleton / sync)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "singleton_sync_errors.py"
    spec = importlib.util.spec_from_file_location("singleton_sync_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_singleton_sync_errors():
    mod = _load()
    cls = getattr(mod, 'SyncSingleton')
    a, b = cls(), cls()
    a.set_value("sync-one")
    assert a is b
    assert b.get_value() == "sync-one"
