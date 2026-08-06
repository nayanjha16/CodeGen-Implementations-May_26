"""Pytest for singleton_email_logging (singleton / email)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "singleton_email_logging.py"
    spec = importlib.util.spec_from_file_location("singleton_email_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_singleton_email_logging():
    mod = _load()
    cls = getattr(mod, 'EmailSingleton')
    a, b = cls(), cls()
    a.set_value("email-one")
    assert a is b
    assert b.get_value() == "email-one"
