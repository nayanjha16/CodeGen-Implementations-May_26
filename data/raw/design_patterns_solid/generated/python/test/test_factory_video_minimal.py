"""Pytest for factory_video_minimal (factory / video)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "factory_video_minimal.py"
    spec = importlib.util.spec_from_file_location("factory_video_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_factory_video_minimal():
    mod = _load()
    f = mod.VideoFactory()
    assert f.create("premium").operate() == "premium-video"
