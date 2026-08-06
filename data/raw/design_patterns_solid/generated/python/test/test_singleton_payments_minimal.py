"""Pytest for singleton_payments_minimal (singleton / payments)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "singleton_payments_minimal.py"
    spec = importlib.util.spec_from_file_location("singleton_payments_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_singleton_payments_minimal():
    mod = _load()
    cls = getattr(mod, 'PaymentsSingleton')
    a, b = cls(), cls()
    a.set_value("payments-one")
    assert a is b
    assert b.get_value() == "payments-one"
