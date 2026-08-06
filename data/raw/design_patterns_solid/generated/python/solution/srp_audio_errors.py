"""DesignPatternsSolid | kind=solid | label=srp | domain=audio | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class AudioRecord:
    id: str
    amount: int

class AudioRepository:
    def save(self, r: AudioRecord) -> str:
        return f"saved-audio:{r.id}"

class AudioFormatter:
    def format(self, r: AudioRecord) -> str:
        return f"{r.id}={r.amount}"
