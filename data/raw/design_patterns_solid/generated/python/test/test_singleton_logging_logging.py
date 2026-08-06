"""Pytest for singleton_logging_logging (singleton / logging)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "singleton_logging_logging.py"
    spec = importlib.util.spec_from_file_location("singleton_logging_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_singleton_logging_logging():
    mod = _load()
    cls = getattr(mod, 'LoggingSingleton')
    a, b = cls(), cls()
    a.set_value("logging-one")
    assert a is b
    assert b.get_value() == "logging-one"
