"""Pytest for ocp_notifications_minimal (ocp / notifications)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "ocp_notifications_minimal.py"
    spec = importlib.util.spec_from_file_location("ocp_notifications_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_ocp_notifications_minimal():
    mod = _load()
    eng = mod.NotificationsPriceEngine(mod.NotificationsTenPercent())
    assert eng.quote(100) == 90
