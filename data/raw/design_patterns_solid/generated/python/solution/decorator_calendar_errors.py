"""DesignPatternsSolid | kind=design_pattern | label=decorator | domain=calendar | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CalendarComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class CalendarCore(CalendarComponent):
    def process(self, input: str) -> str:
        return f"calendar:{input}"

class CalendarUpperDecorator(CalendarComponent):
    def __init__(self, inner: CalendarComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
