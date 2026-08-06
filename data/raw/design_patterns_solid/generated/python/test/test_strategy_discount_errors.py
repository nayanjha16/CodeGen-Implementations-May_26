"""Pytest for strategy_discount_errors (strategy / discount)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "strategy_discount_errors.py"
    spec = importlib.util.spec_from_file_location("strategy_discount_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_strategy_discount_errors():
    mod = _load()
    ctx = mod.DiscountContext(mod.DiscountDiscountStrategy())
    assert ctx.execute(10) == 5
