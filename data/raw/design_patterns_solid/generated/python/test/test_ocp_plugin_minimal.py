"""Pytest for ocp_plugin_minimal (ocp / plugin)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "ocp_plugin_minimal.py"
    spec = importlib.util.spec_from_file_location("ocp_plugin_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_ocp_plugin_minimal():
    mod = _load()
    eng = mod.PluginPriceEngine(mod.PluginTenPercent())
    assert eng.quote(100) == 90
