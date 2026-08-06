"""Pytest for observer_scheduling_errors (observer / scheduling)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "observer_scheduling_errors.py"
    spec = importlib.util.spec_from_file_location("observer_scheduling_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_observer_scheduling_errors():
    mod = _load()
    subj, lis = mod.SchedulingSubject(), mod.SchedulingListener()
    subj.attach(lis)
    subj.notify_all("e")
    assert lis.last == "scheduling:e"
