"""Pytest for dip_shipping_logging (dip / shipping)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "dip_shipping_logging.py"
    spec = importlib.util.spec_from_file_location("dip_shipping_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_dip_shipping_logging():
    mod = _load()
    app = mod.ShippingAppService(mod.ShippingHttpGateway())
    assert app.publish("p") == "http-shipping:p"
