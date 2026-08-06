"""Pytest for factory_billing_minimal (factory / billing)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "factory_billing_minimal.py"
    spec = importlib.util.spec_from_file_location("factory_billing_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_factory_billing_minimal():
    mod = _load()
    f = mod.BillingFactory()
    assert f.create("premium").operate() == "premium-billing"
