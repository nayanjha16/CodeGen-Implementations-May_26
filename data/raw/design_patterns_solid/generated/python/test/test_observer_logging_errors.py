"""Pytest for observer_logging_errors (observer / logging)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "observer_logging_errors.py"
    spec = importlib.util.spec_from_file_location("observer_logging_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_observer_logging_errors():
    mod = _load()
    subj, lis = mod.LoggingSubject(), mod.LoggingListener()
    subj.attach(lis)
    subj.notify_all("e")
    assert lis.last == "logging:e"
