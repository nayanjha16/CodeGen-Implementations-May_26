"""Pytest for dip_editor_errors (dip / editor)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "dip_editor_errors.py"
    spec = importlib.util.spec_from_file_location("dip_editor_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_dip_editor_errors():
    mod = _load()
    app = mod.EditorAppService(mod.EditorHttpGateway())
    assert app.publish("p") == "http-editor:p"
