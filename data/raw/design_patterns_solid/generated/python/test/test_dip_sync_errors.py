"""Pytest for dip_sync_errors (dip / sync)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "dip_sync_errors.py"
    spec = importlib.util.spec_from_file_location("dip_sync_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_dip_sync_errors():
    mod = _load()
    app = mod.SyncAppService(mod.SyncHttpGateway())
    assert app.publish("p") == "http-sync:p"
