"""Pytest for dip_notes_errors (dip / notes)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "dip_notes_errors.py"
    spec = importlib.util.spec_from_file_location("dip_notes_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_dip_notes_errors():
    mod = _load()
    app = mod.NotesAppService(mod.NotesHttpGateway())
    assert app.publish("p") == "http-notes:p"
