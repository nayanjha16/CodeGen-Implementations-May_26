"""Pytest for srp_database_minimal (srp / database)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "srp_database_minimal.py"
    spec = importlib.util.spec_from_file_location("srp_database_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_srp_database_minimal():
    mod = _load()
    r = mod.DatabaseRecord("a", 3)
    assert mod.DatabaseFormatter().format(r) == 'a=3'
