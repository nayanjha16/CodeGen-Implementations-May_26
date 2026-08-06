"""Pytest for observer_wallet_minimal (observer / wallet)."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "observer_wallet_minimal.py"
    spec = importlib.util.spec_from_file_location("observer_wallet_minimal", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_observer_wallet_minimal():
    mod = _load()
    subj, lis = mod.WalletSubject(), mod.WalletListener()
    subj.attach(lis)
    subj.notify_all("e")
    assert lis.last == "wallet:e"
