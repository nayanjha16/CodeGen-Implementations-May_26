"""DesignPatternsSolid | kind=design_pattern | label=state | domain=http | tier=errors"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class HttpState(ABC):
    @abstractmethod
    def handle(self, ctx: "HttpContext") -> str: ...

class HttpOnState(HttpState):
    def handle(self, ctx: "HttpContext") -> str:
        ctx.set_state(HttpOffState())
        return "was-on-http"

class HttpOffState(HttpState):
    def handle(self, ctx: "HttpContext") -> str:
        ctx.set_state(HttpOnState())
        return "was-off-http"

class HttpContext:
    def __init__(self) -> None:
        self.state: HttpState = HttpOffState()

    def set_state(self, state: HttpState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
