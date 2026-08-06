"""Pytest for ocp_payments_logging (ocp / payments)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "ocp_payments_logging.py"
    spec = importlib.util.spec_from_file_location("ocp_payments_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_ocp_payments_logging():
    mod = _load()
    eng = mod.PaymentsPriceEngine(mod.PaymentsTenPercent())
    assert eng.quote(100) == 90
