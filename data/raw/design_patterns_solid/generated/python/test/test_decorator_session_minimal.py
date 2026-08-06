"""Pytest for decorator_session_minimal (decorator / session)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "decorator_session_minimal.py"
    spec = importlib.util.spec_from_file_location("decorator_session_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_decorator_session_minimal():
    mod = _load()
    assert any(isinstance(getattr(mod, n), type) for n in dir(mod) if not n.startswith('_'))
