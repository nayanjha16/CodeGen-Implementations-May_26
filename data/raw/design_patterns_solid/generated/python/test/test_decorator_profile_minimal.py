"""Pytest for decorator_profile_minimal (decorator / profile)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "decorator_profile_minimal.py"
    spec = importlib.util.spec_from_file_location("decorator_profile_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_decorator_profile_minimal():
    mod = _load()
    assert any(isinstance(getattr(mod, n), type) for n in dir(mod) if not n.startswith('_'))
