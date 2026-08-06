"""Pytest for factory_calendar_errors (factory / calendar)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "factory_calendar_errors.py"
    spec = importlib.util.spec_from_file_location("factory_calendar_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_factory_calendar_errors():
    mod = _load()
    f = mod.CalendarFactory()
    assert f.create("premium").operate() == "premium-calendar"
