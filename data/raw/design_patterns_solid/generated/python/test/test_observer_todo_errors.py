"""Pytest for observer_todo_errors (observer / todo)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "observer_todo_errors.py"
    spec = importlib.util.spec_from_file_location("observer_todo_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_observer_todo_errors():
    mod = _load()
    subj, lis = mod.TodoSubject(), mod.TodoListener()
    subj.attach(lis)
    subj.notify_all("e")
    assert lis.last == "todo:e"
