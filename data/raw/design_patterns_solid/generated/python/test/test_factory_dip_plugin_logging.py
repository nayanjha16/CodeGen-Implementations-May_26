"""Pytest for factory_dip_plugin_logging (factory_dip / plugin)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "factory_dip_plugin_logging.py"
    spec = importlib.util.spec_from_file_location("factory_dip_plugin_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_factory_dip_plugin_logging():
    mod = _load()
    assert any(isinstance(getattr(mod, n), type) for n in dir(mod) if not n.startswith('_'))
