"""Pytest for strategy_ocp_todo_logging (strategy_ocp / todo)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "strategy_ocp_todo_logging.py"
    spec = importlib.util.spec_from_file_location("strategy_ocp_todo_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_strategy_ocp_todo_logging():
    mod = _load()
    assert any(isinstance(getattr(mod, n), type) for n in dir(mod) if not n.startswith('_'))
