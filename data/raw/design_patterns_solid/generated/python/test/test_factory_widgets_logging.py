"""Pytest for factory_widgets_logging (factory / widgets)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "factory_widgets_logging.py"
    spec = importlib.util.spec_from_file_location("factory_widgets_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_factory_widgets_logging():
    mod = _load()
    f = mod.WidgetsFactory()
    assert f.create("premium").operate() == "premium-widgets"
