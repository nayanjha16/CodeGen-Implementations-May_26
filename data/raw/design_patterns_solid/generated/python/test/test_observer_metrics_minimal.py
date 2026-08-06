"""Pytest for observer_metrics_minimal (observer / metrics)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "observer_metrics_minimal.py"
    spec = importlib.util.spec_from_file_location("observer_metrics_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_observer_metrics_minimal():
    mod = _load()
    subj, lis = mod.MetricsSubject(), mod.MetricsListener()
    subj.attach(lis)
    subj.notify_all("e")
    assert lis.last == "metrics:e"
