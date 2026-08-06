"""Pytest for srp_video_logging (srp / video)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "srp_video_logging.py"
    spec = importlib.util.spec_from_file_location("srp_video_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_srp_video_logging():
    mod = _load()
    r = mod.VideoRecord("a", 3)
    assert mod.VideoFormatter().format(r) == 'a=3'
