"""DesignPatternsSolid | kind=solid | label=srp | domain=plugin | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class PluginRecord:
    id: str
    amount: int

class PluginRepository:
    def save(self, r: PluginRecord) -> str:
        return f"saved-plugin:{r.id}"

class PluginFormatter:
    def format(self, r: PluginRecord) -> str:
        return f"{r.id}={r.amount}"
