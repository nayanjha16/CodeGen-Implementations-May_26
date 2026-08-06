"""DesignPatternsSolid | kind=solid | label=srp | domain=payments | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class PaymentsRecord:
    id: str
    amount: int

class PaymentsRepository:
    def save(self, r: PaymentsRecord) -> str:
        return f"saved-payments:{r.id}"

class PaymentsFormatter:
    def format(self, r: PaymentsRecord) -> str:
        return f"{r.id}={r.amount}"
