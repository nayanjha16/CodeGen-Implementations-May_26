"""DesignPatternsSolid | kind=solid | label=srp | domain=notes | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class NotesRecord:
    id: str
    amount: int

class NotesRepository:
    def save(self, r: NotesRecord) -> str:
        return f"saved-notes:{r.id}"

class NotesFormatter:
    def format(self, r: NotesRecord) -> str:
        return f"{r.id}={r.amount}"
