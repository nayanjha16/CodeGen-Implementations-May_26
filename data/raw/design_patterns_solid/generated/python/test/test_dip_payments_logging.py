"""Pytest for dip_payments_logging (dip / payments)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "dip_payments_logging.py"
    spec = importlib.util.spec_from_file_location("dip_payments_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_dip_payments_logging():
    mod = _load()
    app = mod.PaymentsAppService(mod.PaymentsHttpGateway())
    assert app.publish("p") == "http-payments:p"
