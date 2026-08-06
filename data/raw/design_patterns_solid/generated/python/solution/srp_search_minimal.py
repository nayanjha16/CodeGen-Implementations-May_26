"""DesignPatternsSolid | kind=solid | label=srp | domain=search | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class SearchRecord:
    id: str
    amount: int

class SearchRepository:
    def save(self, r: SearchRecord) -> str:
        return f"saved-search:{r.id}"

class SearchFormatter:
    def format(self, r: SearchRecord) -> str:
        return f"{r.id}={r.amount}"
