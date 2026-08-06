"""DesignPatternsSolid | kind=solid | label=srp | domain=backup | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class BackupRecord:
    id: str
    amount: int

class BackupRepository:
    def save(self, r: BackupRecord) -> str:
        return f"saved-backup:{r.id}"

class BackupFormatter:
    def format(self, r: BackupRecord) -> str:
        return f"{r.id}={r.amount}"
