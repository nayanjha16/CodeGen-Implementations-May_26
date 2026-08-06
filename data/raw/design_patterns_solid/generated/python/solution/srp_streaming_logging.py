"""DesignPatternsSolid | kind=solid | label=srp | domain=streaming | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class StreamingRecord:
    id: str
    amount: int

class StreamingRepository:
    def save(self, r: StreamingRecord) -> str:
        return f"saved-streaming:{r.id}"

class StreamingFormatter:
    def format(self, r: StreamingRecord) -> str:
        return f"{r.id}={r.amount}"
