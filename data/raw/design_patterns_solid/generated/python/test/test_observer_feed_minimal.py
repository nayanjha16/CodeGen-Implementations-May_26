"""Pytest for observer_feed_minimal (observer / feed)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "observer_feed_minimal.py"
    spec = importlib.util.spec_from_file_location("observer_feed_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_observer_feed_minimal():
    mod = _load()
    subj, lis = mod.FeedSubject(), mod.FeedListener()
    subj.attach(lis)
    subj.notify_all("e")
    assert lis.last == "feed:e"
