"""DesignPatternsSolid | kind=solid | label=srp | domain=auth | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class AuthRecord:
    id: str
    amount: int

class AuthRepository:
    def save(self, r: AuthRecord) -> str:
        return f"saved-auth:{r.id}"

class AuthFormatter:
    def format(self, r: AuthRecord) -> str:
        return f"{r.id}={r.amount}"
