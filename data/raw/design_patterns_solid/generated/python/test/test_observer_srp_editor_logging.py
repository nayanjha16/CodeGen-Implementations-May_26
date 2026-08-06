"""Pytest for observer_srp_editor_logging (observer_srp / editor)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "observer_srp_editor_logging.py"
    spec = importlib.util.spec_from_file_location("observer_srp_editor_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_observer_srp_editor_logging():
    mod = _load()
    assert any(isinstance(getattr(mod, n), type) for n in dir(mod) if not n.startswith('_'))
