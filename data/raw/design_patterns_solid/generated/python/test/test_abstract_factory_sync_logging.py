"""Pytest for abstract_factory_sync_logging (abstract_factory / sync)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "abstract_factory_sync_logging.py"
    spec = importlib.util.spec_from_file_location("abstract_factory_sync_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_abstract_factory_sync_logging():
    mod = _load()
    assert any(isinstance(getattr(mod, n), type) for n in dir(mod) if not n.startswith('_'))
