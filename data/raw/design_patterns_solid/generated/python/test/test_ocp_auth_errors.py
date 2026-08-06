"""Pytest for ocp_auth_errors (ocp / auth)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "ocp_auth_errors.py"
    spec = importlib.util.spec_from_file_location("ocp_auth_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_ocp_auth_errors():
    mod = _load()
    eng = mod.AuthPriceEngine(mod.AuthTenPercent())
    assert eng.quote(100) == 90
