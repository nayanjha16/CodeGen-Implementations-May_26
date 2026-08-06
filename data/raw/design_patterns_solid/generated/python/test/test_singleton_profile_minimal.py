"""Pytest for singleton_profile_minimal (singleton / profile)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "singleton_profile_minimal.py"
    spec = importlib.util.spec_from_file_location("singleton_profile_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_singleton_profile_minimal():
    mod = _load()
    cls = getattr(mod, 'ProfileSingleton')
    a, b = cls(), cls()
    a.set_value("profile-one")
    assert a is b
    assert b.get_value() == "profile-one"
