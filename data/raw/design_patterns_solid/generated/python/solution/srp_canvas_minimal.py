"""DesignPatternsSolid | kind=solid | label=srp | domain=canvas | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class CanvasRecord:
    id: str
    amount: int

class CanvasRepository:
    def save(self, r: CanvasRecord) -> str:
        return f"saved-canvas:{r.id}"

class CanvasFormatter:
    def format(self, r: CanvasRecord) -> str:
        return f"{r.id}={r.amount}"
