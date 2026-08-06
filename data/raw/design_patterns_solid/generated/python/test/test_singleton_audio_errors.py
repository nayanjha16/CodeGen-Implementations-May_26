"""Pytest for singleton_audio_errors (singleton / audio)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "singleton_audio_errors.py"
    spec = importlib.util.spec_from_file_location("singleton_audio_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_singleton_audio_errors():
    mod = _load()
    cls = getattr(mod, 'AudioSingleton')
    a, b = cls(), cls()
    a.set_value("audio-one")
    assert a is b
    assert b.get_value() == "audio-one"
