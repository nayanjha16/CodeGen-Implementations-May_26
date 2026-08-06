"""DesignPatternsSolid | kind=solid | label=srp | domain=feed | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class FeedRecord:
    id: str
    amount: int

class FeedRepository:
    def save(self, r: FeedRecord) -> str:
        return f"saved-feed:{r.id}"

class FeedFormatter:
    def format(self, r: FeedRecord) -> str:
        return f"{r.id}={r.amount}"
