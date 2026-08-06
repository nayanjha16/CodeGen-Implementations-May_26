"""Pytest for observer_email_minimal (observer / email)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "observer_email_minimal.py"
    spec = importlib.util.spec_from_file_location("observer_email_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_observer_email_minimal():
    mod = _load()
    subj, lis = mod.EmailSubject(), mod.EmailListener()
    subj.attach(lis)
    subj.notify_all("e")
    assert lis.last == "email:e"
