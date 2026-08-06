"""Pytest for singleton_widgets_minimal (singleton / widgets)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "singleton_widgets_minimal.py"
    spec = importlib.util.spec_from_file_location("singleton_widgets_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_singleton_widgets_minimal():
    mod = _load()
    cls = getattr(mod, 'WidgetsSingleton')
    a, b = cls(), cls()
    a.set_value("widgets-one")
    assert a is b
    assert b.get_value() == "widgets-one"
