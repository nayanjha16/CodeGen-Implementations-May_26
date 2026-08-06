"""Pytest for singleton_discount_logging (singleton / discount)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "singleton_discount_logging.py"
    spec = importlib.util.spec_from_file_location("singleton_discount_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_singleton_discount_logging():
    mod = _load()
    cls = getattr(mod, 'DiscountSingleton')
    a, b = cls(), cls()
    a.set_value("discount-one")
    assert a is b
    assert b.get_value() == "discount-one"
