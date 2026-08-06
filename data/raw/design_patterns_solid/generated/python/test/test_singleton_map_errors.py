"""Pytest for singleton_map_errors (singleton / map)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "singleton_map_errors.py"
    spec = importlib.util.spec_from_file_location("singleton_map_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_singleton_map_errors():
    mod = _load()
    cls = getattr(mod, 'MapSingleton')
    a, b = cls(), cls()
    a.set_value("map-one")
    assert a is b
    assert b.get_value() == "map-one"
