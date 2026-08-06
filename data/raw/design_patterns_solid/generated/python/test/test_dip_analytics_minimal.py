"""Pytest for dip_analytics_minimal (dip / analytics)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "dip_analytics_minimal.py"
    spec = importlib.util.spec_from_file_location("dip_analytics_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_dip_analytics_minimal():
    mod = _load()
    app = mod.AnalyticsAppService(mod.AnalyticsHttpGateway())
    assert app.publish("p") == "http-analytics:p"
