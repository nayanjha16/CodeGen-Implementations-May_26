"""DesignPatternsSolid | kind=solid | label=srp | domain=cache | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class CacheRecord:
    id: str
    amount: int

class CacheRepository:
    def save(self, r: CacheRecord) -> str:
        return f"saved-cache:{r.id}"

class CacheFormatter:
    def format(self, r: CacheRecord) -> str:
        return f"{r.id}={r.amount}"
