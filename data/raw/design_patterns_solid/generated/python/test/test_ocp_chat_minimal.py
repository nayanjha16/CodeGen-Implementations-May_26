"""Pytest for ocp_chat_minimal (ocp / chat)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "ocp_chat_minimal.py"
    spec = importlib.util.spec_from_file_location("ocp_chat_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_ocp_chat_minimal():
    mod = _load()
    eng = mod.ChatPriceEngine(mod.ChatTenPercent())
    assert eng.quote(100) == 90
