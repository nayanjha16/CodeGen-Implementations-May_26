"""Pytest for srp_notes_errors (srp / notes)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "srp_notes_errors.py"
    spec = importlib.util.spec_from_file_location("srp_notes_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_srp_notes_errors():
    mod = _load()
    r = mod.NotesRecord("a", 3)
    assert mod.NotesFormatter().format(r) == 'a=3'
