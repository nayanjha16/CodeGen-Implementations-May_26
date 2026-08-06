"""Pytest for factory_audio_errors (factory / audio)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "factory_audio_errors.py"
    spec = importlib.util.spec_from_file_location("factory_audio_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_factory_audio_errors():
    mod = _load()
    f = mod.AudioFactory()
    assert f.create("premium").operate() == "premium-audio"
