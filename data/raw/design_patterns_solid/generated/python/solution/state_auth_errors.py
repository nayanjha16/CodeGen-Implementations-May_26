"""DesignPatternsSolid | kind=design_pattern | label=state | domain=auth | tier=errors"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class AuthState(ABC):
    @abstractmethod
    def handle(self, ctx: "AuthContext") -> str: ...

class AuthOnState(AuthState):
    def handle(self, ctx: "AuthContext") -> str:
        ctx.set_state(AuthOffState())
        return "was-on-auth"

class AuthOffState(AuthState):
    def handle(self, ctx: "AuthContext") -> str:
        ctx.set_state(AuthOnState())
        return "was-off-auth"

class AuthContext:
    def __init__(self) -> None:
        self.state: AuthState = AuthOffState()

    def set_state(self, state: AuthState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
