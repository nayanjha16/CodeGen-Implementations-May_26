"""Pytest for observer_discount_errors (observer / discount)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "observer_discount_errors.py"
    spec = importlib.util.spec_from_file_location("observer_discount_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_observer_discount_errors():
    mod = _load()
    subj, lis = mod.DiscountSubject(), mod.DiscountListener()
    subj.attach(lis)
    subj.notify_all("e")
    assert lis.last == "discount:e"
