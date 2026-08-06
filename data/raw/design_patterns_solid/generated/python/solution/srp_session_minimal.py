"""DesignPatternsSolid | kind=solid | label=srp | domain=session | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class SessionRecord:
    id: str
    amount: int

class SessionRepository:
    def save(self, r: SessionRecord) -> str:
        return f"saved-session:{r.id}"

class SessionFormatter:
    def format(self, r: SessionRecord) -> str:
        return f"{r.id}={r.amount}"
