"""DesignPatternsSolid | kind=solid | label=srp | domain=logging | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class LoggingRecord:
    id: str
    amount: int

class LoggingRepository:
    def save(self, r: LoggingRecord) -> str:
        return f"saved-logging:{r.id}"

class LoggingFormatter:
    def format(self, r: LoggingRecord) -> str:
        return f"{r.id}={r.amount}"
