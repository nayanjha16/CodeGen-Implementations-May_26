"""Pytest for singleton_analytics_logging (singleton / analytics)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "singleton_analytics_logging.py"
    spec = importlib.util.spec_from_file_location("singleton_analytics_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_singleton_analytics_logging():
    mod = _load()
    cls = getattr(mod, 'AnalyticsSingleton')
    a, b = cls(), cls()
    a.set_value("analytics-one")
    assert a is b
    assert b.get_value() == "analytics-one"
