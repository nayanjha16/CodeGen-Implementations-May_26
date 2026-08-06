"""Pytest for ocp_report_logging (ocp / report)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "ocp_report_logging.py"
    spec = importlib.util.spec_from_file_location("ocp_report_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_ocp_report_logging():
    mod = _load()
    eng = mod.ReportPriceEngine(mod.ReportTenPercent())
    assert eng.quote(100) == 90
