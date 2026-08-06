"""Pytest for strategy_logging_minimal (strategy / logging)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "strategy_logging_minimal.py"
    spec = importlib.util.spec_from_file_location("strategy_logging_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_strategy_logging_minimal():
    mod = _load()
    ctx = mod.LoggingContext(mod.LoggingDiscountStrategy())
    assert ctx.execute(10) == 5
