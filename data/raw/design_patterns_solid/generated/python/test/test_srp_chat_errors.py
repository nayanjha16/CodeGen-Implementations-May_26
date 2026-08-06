"""Pytest for srp_chat_errors (srp / chat)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "srp_chat_errors.py"
    spec = importlib.util.spec_from_file_location("srp_chat_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_srp_chat_errors():
    mod = _load()
    r = mod.ChatRecord("a", 3)
    assert mod.ChatFormatter().format(r) == 'a=3'
