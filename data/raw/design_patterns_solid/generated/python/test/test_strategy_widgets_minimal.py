"""Pytest for strategy_widgets_minimal (strategy / widgets)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "strategy_widgets_minimal.py"
    spec = importlib.util.spec_from_file_location("strategy_widgets_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_strategy_widgets_minimal():
    mod = _load()
    ctx = mod.WidgetsContext(mod.WidgetsDiscountStrategy())
    assert ctx.execute(10) == 5
