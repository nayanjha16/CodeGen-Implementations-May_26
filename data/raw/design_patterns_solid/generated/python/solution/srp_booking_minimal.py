"""DesignPatternsSolid | kind=solid | label=srp | domain=booking | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class BookingRecord:
    id: str
    amount: int

class BookingRepository:
    def save(self, r: BookingRecord) -> str:
        return f"saved-booking:{r.id}"

class BookingFormatter:
    def format(self, r: BookingRecord) -> str:
        return f"{r.id}={r.amount}"
