"""Pytest for singleton_review_logging (singleton / review)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "singleton_review_logging.py"
    spec = importlib.util.spec_from_file_location("singleton_review_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_singleton_review_logging():
    mod = _load()
    cls = getattr(mod, 'ReviewSingleton')
    a, b = cls(), cls()
    a.set_value("review-one")
    assert a is b
    assert b.get_value() == "review-one"
