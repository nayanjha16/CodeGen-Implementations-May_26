"""Pytest for ocp_sync_errors (ocp / sync)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "ocp_sync_errors.py"
    spec = importlib.util.spec_from_file_location("ocp_sync_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_ocp_sync_errors():
    mod = _load()
    eng = mod.SyncPriceEngine(mod.SyncTenPercent())
    assert eng.quote(100) == 90
