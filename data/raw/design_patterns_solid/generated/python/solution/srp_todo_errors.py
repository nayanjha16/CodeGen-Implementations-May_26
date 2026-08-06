"""DesignPatternsSolid | kind=solid | label=srp | domain=todo | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class TodoRecord:
    id: str
    amount: int

class TodoRepository:
    def save(self, r: TodoRecord) -> str:
        return f"saved-todo:{r.id}"

class TodoFormatter:
    def format(self, r: TodoRecord) -> str:
        return f"{r.id}={r.amount}"
