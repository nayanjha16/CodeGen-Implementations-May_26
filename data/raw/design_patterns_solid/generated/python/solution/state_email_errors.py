"""DesignPatternsSolid | kind=design_pattern | label=state | domain=email | tier=errors"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class EmailState(ABC):
    @abstractmethod
    def handle(self, ctx: "EmailContext") -> str: ...

class EmailOnState(EmailState):
    def handle(self, ctx: "EmailContext") -> str:
        ctx.set_state(EmailOffState())
        return "was-on-email"

class EmailOffState(EmailState):
    def handle(self, ctx: "EmailContext") -> str:
        ctx.set_state(EmailOnState())
        return "was-off-email"

class EmailContext:
    def __init__(self) -> None:
        self.state: EmailState = EmailOffState()

    def set_state(self, state: EmailState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
