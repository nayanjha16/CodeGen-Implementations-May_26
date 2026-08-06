"""DesignPatternsSolid | kind=solid | label=srp | domain=metrics | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class MetricsRecord:
    id: str
    amount: int

class MetricsRepository:
    def save(self, r: MetricsRecord) -> str:
        return f"saved-metrics:{r.id}"

class MetricsFormatter:
    def format(self, r: MetricsRecord) -> str:
        return f"{r.id}={r.amount}"
