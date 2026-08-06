"""Pytest for strategy_scheduling_logging (strategy / scheduling)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "strategy_scheduling_logging.py"
    spec = importlib.util.spec_from_file_location("strategy_scheduling_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_strategy_scheduling_logging():
    mod = _load()
    ctx = mod.SchedulingContext(mod.SchedulingDiscountStrategy())
    assert ctx.execute(10) == 5
