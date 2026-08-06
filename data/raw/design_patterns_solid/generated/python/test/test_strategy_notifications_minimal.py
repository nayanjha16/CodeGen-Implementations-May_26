"""Pytest for strategy_notifications_minimal (strategy / notifications)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "strategy_notifications_minimal.py"
    spec = importlib.util.spec_from_file_location("strategy_notifications_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_strategy_notifications_minimal():
    mod = _load()
    ctx = mod.NotificationsContext(mod.NotificationsDiscountStrategy())
    assert ctx.execute(10) == 5
