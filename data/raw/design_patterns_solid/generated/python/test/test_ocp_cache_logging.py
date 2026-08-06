"""Pytest for ocp_cache_logging (ocp / cache)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "ocp_cache_logging.py"
    spec = importlib.util.spec_from_file_location("ocp_cache_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_ocp_cache_logging():
    mod = _load()
    eng = mod.CachePriceEngine(mod.CacheTenPercent())
    assert eng.quote(100) == 90
