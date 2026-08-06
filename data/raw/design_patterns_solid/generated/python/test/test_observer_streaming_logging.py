"""Pytest for observer_streaming_logging (observer / streaming)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "observer_streaming_logging.py"
    spec = importlib.util.spec_from_file_location("observer_streaming_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_observer_streaming_logging():
    mod = _load()
    subj, lis = mod.StreamingSubject(), mod.StreamingListener()
    subj.attach(lis)
    subj.notify_all("e")
    assert lis.last == "streaming:e"
