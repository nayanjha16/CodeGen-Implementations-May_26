"""DesignPatternsSolid | kind=solid | label=srp | domain=notifications | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class NotificationsRecord:
    id: str
    amount: int

class NotificationsRepository:
    def save(self, r: NotificationsRecord) -> str:
        return f"saved-notifications:{r.id}"

class NotificationsFormatter:
    def format(self, r: NotificationsRecord) -> str:
        return f"{r.id}={r.amount}"
