"""Pytest for singleton_search_minimal (singleton / search)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "singleton_search_minimal.py"
    spec = importlib.util.spec_from_file_location("singleton_search_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_singleton_search_minimal():
    mod = _load()
    cls = getattr(mod, 'SearchSingleton')
    a, b = cls(), cls()
    a.set_value("search-one")
    assert a is b
    assert b.get_value() == "search-one"
