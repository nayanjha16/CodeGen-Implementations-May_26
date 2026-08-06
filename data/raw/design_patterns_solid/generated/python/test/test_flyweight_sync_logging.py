"""Pytest for flyweight_sync_logging (flyweight / sync)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "flyweight_sync_logging.py"
    spec = importlib.util.spec_from_file_location("flyweight_sync_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_flyweight_sync_logging():
    mod = _load()
    assert any(isinstance(getattr(mod, n), type) for n in dir(mod) if not n.startswith('_'))
