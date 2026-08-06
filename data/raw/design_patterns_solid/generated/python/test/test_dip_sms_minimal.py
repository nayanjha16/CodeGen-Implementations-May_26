"""Pytest for dip_sms_minimal (dip / sms)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "dip_sms_minimal.py"
    spec = importlib.util.spec_from_file_location("dip_sms_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_dip_sms_minimal():
    mod = _load()
    app = mod.SmsAppService(mod.SmsHttpGateway())
    assert app.publish("p") == "http-sms:p"
