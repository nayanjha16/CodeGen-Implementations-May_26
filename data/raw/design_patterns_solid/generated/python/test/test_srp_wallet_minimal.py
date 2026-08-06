"""Pytest for srp_wallet_minimal (srp / wallet)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "srp_wallet_minimal.py"
    spec = importlib.util.spec_from_file_location("srp_wallet_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_srp_wallet_minimal():
    mod = _load()
    r = mod.WalletRecord("a", 3)
    assert mod.WalletFormatter().format(r) == 'a=3'
