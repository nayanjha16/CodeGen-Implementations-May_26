"""Pytest for factory_review_logging (factory / review)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "factory_review_logging.py"
    spec = importlib.util.spec_from_file_location("factory_review_logging", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_factory_review_logging():
    mod = _load()
    f = mod.ReviewFactory()
    assert f.create("premium").operate() == "premium-review"
