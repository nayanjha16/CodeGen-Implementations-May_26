"""DesignPatternsSolid | kind=solid | label=srp | domain=sms | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class SmsRecord:
    id: str
    amount: int

class SmsRepository:
    def save(self, r: SmsRecord) -> str:
        return f"saved-sms:{r.id}"

class SmsFormatter:
    def format(self, r: SmsRecord) -> str:
        return f"{r.id}={r.amount}"
