"""DesignPatternsSolid | kind=design_pattern | label=state | domain=session | tier=errors"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class SessionState(ABC):
    @abstractmethod
    def handle(self, ctx: "SessionContext") -> str: ...

class SessionOnState(SessionState):
    def handle(self, ctx: "SessionContext") -> str:
        ctx.set_state(SessionOffState())
        return "was-on-session"

class SessionOffState(SessionState):
    def handle(self, ctx: "SessionContext") -> str:
        ctx.set_state(SessionOnState())
        return "was-off-session"

class SessionContext:
    def __init__(self) -> None:
        self.state: SessionState = SessionOffState()

    def set_state(self, state: SessionState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
