"""Pytest for dip_cart_minimal (dip / cart)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "dip_cart_minimal.py"
    spec = importlib.util.spec_from_file_location("dip_cart_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_dip_cart_minimal():
    mod = _load()
    app = mod.CartAppService(mod.CartHttpGateway())
    assert app.publish("p") == "http-cart:p"
