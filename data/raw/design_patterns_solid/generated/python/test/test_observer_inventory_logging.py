"""Pytest for observer_inventory_logging (observer / inventory)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "observer_inventory_logging.py"
    spec = importlib.util.spec_from_file_location("observer_inventory_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_observer_inventory_logging():
    mod = _load()
    subj, lis = mod.InventorySubject(), mod.InventoryListener()
    subj.attach(lis)
    subj.notify_all("e")
    assert lis.last == "inventory:e"
