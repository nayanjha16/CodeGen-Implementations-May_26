"""Pytest for observer_report_logging (observer / report)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "observer_report_logging.py"
    spec = importlib.util.spec_from_file_location("observer_report_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_observer_report_logging():
    mod = _load()
    subj, lis = mod.ReportSubject(), mod.ReportListener()
    subj.attach(lis)
    subj.notify_all("e")
    assert lis.last == "report:e"
