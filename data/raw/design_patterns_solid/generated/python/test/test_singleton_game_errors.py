"""Pytest for singleton_game_errors (singleton / game)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "singleton_game_errors.py"
    spec = importlib.util.spec_from_file_location("singleton_game_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_singleton_game_errors():
    mod = _load()
    cls = getattr(mod, 'GameSingleton')
    a, b = cls(), cls()
    a.set_value("game-one")
    assert a is b
    assert b.get_value() == "game-one"
