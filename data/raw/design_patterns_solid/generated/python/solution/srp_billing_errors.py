"""DesignPatternsSolid | kind=solid | label=srp | domain=billing | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class BillingRecord:
    id: str
    amount: int

class BillingRepository:
    def save(self, r: BillingRecord) -> str:
        return f"saved-billing:{r.id}"

class BillingFormatter:
    def format(self, r: BillingRecord) -> str:
        return f"{r.id}={r.amount}"
