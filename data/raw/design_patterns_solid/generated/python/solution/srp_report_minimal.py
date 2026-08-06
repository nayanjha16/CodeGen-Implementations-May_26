"""DesignPatternsSolid | kind=solid | label=srp | domain=report | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class ReportRecord:
    id: str
    amount: int

class ReportRepository:
    def save(self, r: ReportRecord) -> str:
        return f"saved-report:{r.id}"

class ReportFormatter:
    def format(self, r: ReportRecord) -> str:
        return f"{r.id}={r.amount}"
