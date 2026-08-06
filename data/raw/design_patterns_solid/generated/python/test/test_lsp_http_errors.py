"""Pytest for lsp_http_errors (lsp / http)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "lsp_http_errors.py"
    spec = importlib.util.spec_from_file_location("lsp_http_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_lsp_http_errors():
    mod = _load()
    assert any(isinstance(getattr(mod, n), type) for n in dir(mod) if not n.startswith('_'))
