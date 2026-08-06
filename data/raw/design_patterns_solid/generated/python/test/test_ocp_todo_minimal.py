"""Pytest for ocp_todo_minimal (ocp / todo)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "ocp_todo_minimal.py"
    spec = importlib.util.spec_from_file_location("ocp_todo_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_ocp_todo_minimal():
    mod = _load()
    eng = mod.TodoPriceEngine(mod.TodoTenPercent())
    assert eng.quote(100) == 90
