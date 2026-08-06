"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=ticket | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TicketComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class TicketCore(TicketComponent):
    def process(self, input: str) -> str:
        return f"ticket:{input}"

class TicketUpperDecorator(TicketComponent):
    def __init__(self, inner: TicketComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
