"""Pytest for srp_logging_minimal (srp / logging)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "srp_logging_minimal.py"
    spec = importlib.util.spec_from_file_location("srp_logging_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_srp_logging_minimal():
    mod = _load()
    r = mod.LoggingRecord("a", 3)
    assert mod.LoggingFormatter().format(r) == 'a=3'
