"""Pytest for factory_todo_errors (factory / todo)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "factory_todo_errors.py"
    spec = importlib.util.spec_from_file_location("factory_todo_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_factory_todo_errors():
    mod = _load()
    f = mod.TodoFactory()
    assert f.create("premium").operate() == "premium-todo"
