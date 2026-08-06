"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=notifications | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class NotificationsComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class NotificationsCore(NotificationsComponent):
    def process(self, input: str) -> str:
        return f"notifications:{input}"

class NotificationsUpperDecorator(NotificationsComponent):
    def __init__(self, inner: NotificationsComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
