"""DesignPatternsSolid | kind=design_pattern | label=observer | domain=calendar | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CalendarObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class CalendarSubject:
    def __init__(self) -> None:
        self.observers: list[CalendarObserver] = []
        self.events: list[str] = []

    def attach(self, o: CalendarObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class CalendarListener(CalendarObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"calendar:{event}"
