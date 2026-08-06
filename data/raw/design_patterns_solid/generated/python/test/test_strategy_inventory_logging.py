"""Pytest for strategy_inventory_logging (strategy / inventory)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "strategy_inventory_logging.py"
    spec = importlib.util.spec_from_file_location("strategy_inventory_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_strategy_inventory_logging():
    mod = _load()
    ctx = mod.InventoryContext(mod.InventoryDiscountStrategy())
    assert ctx.execute(10) == 5
