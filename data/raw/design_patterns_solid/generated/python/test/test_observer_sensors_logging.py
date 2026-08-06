"""Pytest for observer_sensors_logging (observer / sensors)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "observer_sensors_logging.py"
    spec = importlib.util.spec_from_file_location("observer_sensors_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_observer_sensors_logging():
    mod = _load()
    subj, lis = mod.SensorsSubject(), mod.SensorsListener()
    subj.attach(lis)
    subj.notify_all("e")
    assert lis.last == "sensors:e"
