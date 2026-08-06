"""Pytest for singleton_streaming_errors (singleton / streaming)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "singleton_streaming_errors.py"
    spec = importlib.util.spec_from_file_location("singleton_streaming_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_singleton_streaming_errors():
    mod = _load()
    cls = getattr(mod, 'StreamingSingleton')
    a, b = cls(), cls()
    a.set_value("streaming-one")
    assert a is b
    assert b.get_value() == "streaming-one"
