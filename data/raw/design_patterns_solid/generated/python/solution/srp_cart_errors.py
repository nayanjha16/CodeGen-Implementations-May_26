"""DesignPatternsSolid | kind=solid | label=srp | domain=cart | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class CartRecord:
    id: str
    amount: int

class CartRepository:
    def save(self, r: CartRecord) -> str:
        return f"saved-cart:{r.id}"

class CartFormatter:
    def format(self, r: CartRecord) -> str:
        return f"{r.id}={r.amount}"
