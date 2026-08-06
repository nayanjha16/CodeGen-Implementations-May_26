"""DesignPatternsSolid | kind=solid | label=srp | domain=ticket | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class TicketRecord:
    id: str
    amount: int

class TicketRepository:
    def save(self, r: TicketRecord) -> str:
        return f"saved-ticket:{r.id}"

class TicketFormatter:
    def format(self, r: TicketRecord) -> str:
        return f"{r.id}={r.amount}"
