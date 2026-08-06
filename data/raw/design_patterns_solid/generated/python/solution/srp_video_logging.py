"""DesignPatternsSolid | kind=solid | label=srp | domain=video | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class VideoRecord:
    id: str
    amount: int

class VideoRepository:
    def save(self, r: VideoRecord) -> str:
        return f"saved-video:{r.id}"

class VideoFormatter:
    def format(self, r: VideoRecord) -> str:
        return f"{r.id}={r.amount}"
