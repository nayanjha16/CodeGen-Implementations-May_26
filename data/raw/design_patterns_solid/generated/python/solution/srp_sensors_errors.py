"""DesignPatternsSolid | kind=solid | label=srp | domain=sensors | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class SensorsRecord:
    id: str
    amount: int

class SensorsRepository:
    def save(self, r: SensorsRecord) -> str:
        return f"saved-sensors:{r.id}"

class SensorsFormatter:
    def format(self, r: SensorsRecord) -> str:
        return f"{r.id}={r.amount}"
