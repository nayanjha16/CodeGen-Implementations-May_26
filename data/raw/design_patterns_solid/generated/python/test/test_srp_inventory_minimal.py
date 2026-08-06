"""Pytest for srp_inventory_minimal (srp / inventory)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "srp_inventory_minimal.py"
    spec = importlib.util.spec_from_file_location("srp_inventory_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_srp_inventory_minimal():
    mod = _load()
    r = mod.InventoryRecord("a", 3)
    assert mod.InventoryFormatter().format(r) == 'a=3'
