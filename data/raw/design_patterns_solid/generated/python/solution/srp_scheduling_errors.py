"""DesignPatternsSolid | kind=solid | label=srp | domain=scheduling | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class SchedulingRecord:
    id: str
    amount: int

class SchedulingRepository:
    def save(self, r: SchedulingRecord) -> str:
        return f"saved-scheduling:{r.id}"

class SchedulingFormatter:
    def format(self, r: SchedulingRecord) -> str:
        return f"{r.id}={r.amount}"
