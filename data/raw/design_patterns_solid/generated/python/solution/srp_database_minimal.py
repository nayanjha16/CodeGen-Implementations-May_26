"""DesignPatternsSolid | kind=solid | label=srp | domain=database | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class DatabaseRecord:
    id: str
    amount: int

class DatabaseRepository:
    def save(self, r: DatabaseRecord) -> str:
        return f"saved-database:{r.id}"

class DatabaseFormatter:
    def format(self, r: DatabaseRecord) -> str:
        return f"{r.id}={r.amount}"
