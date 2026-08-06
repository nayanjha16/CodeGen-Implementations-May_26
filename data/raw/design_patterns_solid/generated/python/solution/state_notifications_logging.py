"""DesignPatternsSolid | kind=design_pattern | label=state | domain=notifications | tier=logging"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class NotificationsState(ABC):
    @abstractmethod
    def handle(self, ctx: "NotificationsContext") -> str: ...

class NotificationsOnState(NotificationsState):
    def handle(self, ctx: "NotificationsContext") -> str:
        ctx.set_state(NotificationsOffState())
        return "was-on-notifications"

class NotificationsOffState(NotificationsState):
    def handle(self, ctx: "NotificationsContext") -> str:
        ctx.set_state(NotificationsOnState())
        return "was-off-notifications"

class NotificationsContext:
    def __init__(self) -> None:
        self.state: NotificationsState = NotificationsOffState()

    def set_state(self, state: NotificationsState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
