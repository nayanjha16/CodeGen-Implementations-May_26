"""Pytest for dip_config_logging (dip / config)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "dip_config_logging.py"
    spec = importlib.util.spec_from_file_location("dip_config_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_dip_config_logging():
    mod = _load()
    app = mod.ConfigAppService(mod.ConfigHttpGateway())
    assert app.publish("p") == "http-config:p"
