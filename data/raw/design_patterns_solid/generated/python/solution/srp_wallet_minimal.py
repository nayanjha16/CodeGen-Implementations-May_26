"""DesignPatternsSolid | kind=solid | label=srp | domain=wallet | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class WalletRecord:
    id: str
    amount: int

class WalletRepository:
    def save(self, r: WalletRecord) -> str:
        return f"saved-wallet:{r.id}"

class WalletFormatter:
    def format(self, r: WalletRecord) -> str:
        return f"{r.id}={r.amount}"
