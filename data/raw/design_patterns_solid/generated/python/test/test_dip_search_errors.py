"""Pytest for dip_search_errors (dip / search)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "dip_search_errors.py"
    spec = importlib.util.spec_from_file_location("dip_search_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_dip_search_errors():
    mod = _load()
    app = mod.SearchAppService(mod.SearchHttpGateway())
    assert app.publish("p") == "http-search:p"
