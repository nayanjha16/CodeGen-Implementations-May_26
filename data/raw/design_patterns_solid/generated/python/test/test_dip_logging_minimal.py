"""Pytest for dip_logging_minimal (dip / logging)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "dip_logging_minimal.py"
    spec = importlib.util.spec_from_file_location("dip_logging_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_dip_logging_minimal():
    mod = _load()
    app = mod.LoggingAppService(mod.LoggingHttpGateway())
    assert app.publish("p") == "http-logging:p"
