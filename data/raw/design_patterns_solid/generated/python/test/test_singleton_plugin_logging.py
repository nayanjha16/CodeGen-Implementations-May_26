"""Pytest for singleton_plugin_logging (singleton / plugin)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "singleton_plugin_logging.py"
    spec = importlib.util.spec_from_file_location("singleton_plugin_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_singleton_plugin_logging():
    mod = _load()
    cls = getattr(mod, 'PluginSingleton')
    a, b = cls(), cls()
    a.set_value("plugin-one")
    assert a is b
    assert b.get_value() == "plugin-one"
