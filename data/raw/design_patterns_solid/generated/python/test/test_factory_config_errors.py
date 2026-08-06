"""Pytest for factory_config_errors (factory / config)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "factory_config_errors.py"
    spec = importlib.util.spec_from_file_location("factory_config_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_factory_config_errors():
    mod = _load()
    f = mod.ConfigFactory()
    assert f.create("premium").operate() == "premium-config"
