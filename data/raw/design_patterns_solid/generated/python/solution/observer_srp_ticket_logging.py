"""DesignPatternsSolid | kind=combo | label=observer+srp | domain=ticket | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TicketObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class TicketSubject:
    def __init__(self) -> None:
        self.observers: list[TicketObserver] = []
        self.events: list[str] = []

    def attach(self, o: TicketObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class TicketListener(TicketObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"ticket:{event}"
