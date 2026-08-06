"""Pytest for singleton_sensors_errors (singleton / sensors)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "singleton_sensors_errors.py"
    spec = importlib.util.spec_from_file_location("singleton_sensors_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_singleton_sensors_errors():
    mod = _load()
    cls = getattr(mod, 'SensorsSingleton')
    a, b = cls(), cls()
    a.set_value("sensors-one")
    assert a is b
    assert b.get_value() == "sensors-one"
