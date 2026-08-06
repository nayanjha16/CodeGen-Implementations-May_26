"""Pytest for dip_review_minimal (dip / review)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "dip_review_minimal.py"
    spec = importlib.util.spec_from_file_location("dip_review_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_dip_review_minimal():
    mod = _load()
    app = mod.ReviewAppService(mod.ReviewHttpGateway())
    assert app.publish("p") == "http-review:p"
