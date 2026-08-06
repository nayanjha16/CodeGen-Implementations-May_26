"""DesignPatternsSolid | kind=solid | label=srp | domain=inventory | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class InventoryRecord:
    id: str
    amount: int

class InventoryRepository:
    def save(self, r: InventoryRecord) -> str:
        return f"saved-inventory:{r.id}"

class InventoryFormatter:
    def format(self, r: InventoryRecord) -> str:
        return f"{r.id}={r.amount}"
