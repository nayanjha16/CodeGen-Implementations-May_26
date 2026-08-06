"""Pytest for strategy_feed_minimal (strategy / feed)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "strategy_feed_minimal.py"
    spec = importlib.util.spec_from_file_location("strategy_feed_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_strategy_feed_minimal():
    mod = _load()
    ctx = mod.FeedContext(mod.FeedDiscountStrategy())
    assert ctx.execute(10) == 5
