"""DesignPatternsSolid | kind=solid | label=srp | domain=http | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class HttpRecord:
    id: str
    amount: int

class HttpRepository:
    def save(self, r: HttpRecord) -> str:
        return f"saved-http:{r.id}"

class HttpFormatter:
    def format(self, r: HttpRecord) -> str:
        return f"{r.id}={r.amount}"
