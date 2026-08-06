"""Pytest for strategy_notes_minimal (strategy / notes)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "strategy_notes_minimal.py"
    spec = importlib.util.spec_from_file_location("strategy_notes_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_strategy_notes_minimal():
    mod = _load()
    ctx = mod.NotesContext(mod.NotesDiscountStrategy())
    assert ctx.execute(10) == 5
