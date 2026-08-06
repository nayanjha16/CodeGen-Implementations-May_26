"""DesignPatternsSolid | kind=design_pattern | label=state | domain=logging | tier=minimal"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class LoggingState(ABC):
    @abstractmethod
    def handle(self, ctx: "LoggingContext") -> str: ...

class LoggingOnState(LoggingState):
    def handle(self, ctx: "LoggingContext") -> str:
        ctx.set_state(LoggingOffState())
        return "was-on-logging"

class LoggingOffState(LoggingState):
    def handle(self, ctx: "LoggingContext") -> str:
        ctx.set_state(LoggingOnState())
        return "was-off-logging"

class LoggingContext:
    def __init__(self) -> None:
        self.state: LoggingState = LoggingOffState()

    def set_state(self, state: LoggingState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
