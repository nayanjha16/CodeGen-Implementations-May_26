"""Pytest for singleton_feed_minimal (singleton / feed)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "singleton_feed_minimal.py"
    spec = importlib.util.spec_from_file_location("singleton_feed_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_singleton_feed_minimal():
    mod = _load()
    cls = getattr(mod, 'FeedSingleton')
    a, b = cls(), cls()
    a.set_value("feed-one")
    assert a is b
    assert b.get_value() == "feed-one"
