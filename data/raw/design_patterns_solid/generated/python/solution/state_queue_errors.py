"""DesignPatternsSolid | kind=design_pattern | label=state | domain=queue | tier=errors"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class QueueState(ABC):
    @abstractmethod
    def handle(self, ctx: "QueueContext") -> str: ...

class QueueOnState(QueueState):
    def handle(self, ctx: "QueueContext") -> str:
        ctx.set_state(QueueOffState())
        return "was-on-queue"

class QueueOffState(QueueState):
    def handle(self, ctx: "QueueContext") -> str:
        ctx.set_state(QueueOnState())
        return "was-off-queue"

class QueueContext:
    def __init__(self) -> None:
        self.state: QueueState = QueueOffState()

    def set_state(self, state: QueueState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
