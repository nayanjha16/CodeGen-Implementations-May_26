"""Pytest for observer_canvas_logging (observer / canvas)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "observer_canvas_logging.py"
    spec = importlib.util.spec_from_file_location("observer_canvas_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_observer_canvas_logging():
    mod = _load()
    subj, lis = mod.CanvasSubject(), mod.CanvasListener()
    subj.attach(lis)
    subj.notify_all("e")
    assert lis.last == "canvas:e"
