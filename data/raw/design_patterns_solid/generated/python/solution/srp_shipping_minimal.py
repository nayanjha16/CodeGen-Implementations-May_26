"""DesignPatternsSolid | kind=solid | label=srp | domain=shipping | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class ShippingRecord:
    id: str
    amount: int

class ShippingRepository:
    def save(self, r: ShippingRecord) -> str:
        return f"saved-shipping:{r.id}"

class ShippingFormatter:
    def format(self, r: ShippingRecord) -> str:
        return f"{r.id}={r.amount}"
