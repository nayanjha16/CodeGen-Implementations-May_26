"""Pytest for chain_of_responsibility_config_errors (chain_of_responsibility / config)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "chain_of_responsibility_config_errors.py"
    spec = importlib.util.spec_from_file_location("chain_of_responsibility_config_errors", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_chain_of_responsibility_config_errors():
    mod = _load()
    assert any(isinstance(getattr(mod, n), type) for n in dir(mod) if not n.startswith('_'))
