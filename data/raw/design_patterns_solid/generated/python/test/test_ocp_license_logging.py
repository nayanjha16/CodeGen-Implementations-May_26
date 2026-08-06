"""Pytest for ocp_license_logging (ocp / license)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "ocp_license_logging.py"
    spec = importlib.util.spec_from_file_location("ocp_license_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_ocp_license_logging():
    mod = _load()
    eng = mod.LicensePriceEngine(mod.LicenseTenPercent())
    assert eng.quote(100) == 90
