"""DesignPatternsSolid | kind=solid | label=srp | domain=chat | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class ChatRecord:
    id: str
    amount: int

class ChatRepository:
    def save(self, r: ChatRecord) -> str:
        return f"saved-chat:{r.id}"

class ChatFormatter:
    def format(self, r: ChatRecord) -> str:
        return f"{r.id}={r.amount}"
