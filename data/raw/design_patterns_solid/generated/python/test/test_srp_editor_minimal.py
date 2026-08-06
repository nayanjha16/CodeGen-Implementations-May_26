"""Pytest for srp_editor_minimal (srp / editor)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "srp_editor_minimal.py"
    spec = importlib.util.spec_from_file_location("srp_editor_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_srp_editor_minimal():
    mod = _load()
    r = mod.EditorRecord("a", 3)
    assert mod.EditorFormatter().format(r) == 'a=3'
