"""Pytest for dip_video_logging (dip / video)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "dip_video_logging.py"
    spec = importlib.util.spec_from_file_location("dip_video_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_dip_video_logging():
    mod = _load()
    app = mod.VideoAppService(mod.VideoHttpGateway())
    assert app.publish("p") == "http-video:p"
