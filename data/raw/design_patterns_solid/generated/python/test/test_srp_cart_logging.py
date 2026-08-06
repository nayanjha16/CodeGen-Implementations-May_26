"""Pytest for srp_cart_logging (srp / cart)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "srp_cart_logging.py"
    spec = importlib.util.spec_from_file_location("srp_cart_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_srp_cart_logging():
    mod = _load()
    r = mod.CartRecord("a", 3)
    assert mod.CartFormatter().format(r) == 'a=3'
