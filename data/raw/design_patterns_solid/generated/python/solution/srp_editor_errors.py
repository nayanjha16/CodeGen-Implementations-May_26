"""DesignPatternsSolid | kind=solid | label=srp | domain=editor | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class EditorRecord:
    id: str
    amount: int

class EditorRepository:
    def save(self, r: EditorRecord) -> str:
        return f"saved-editor:{r.id}"

class EditorFormatter:
    def format(self, r: EditorRecord) -> str:
        return f"{r.id}={r.amount}"
