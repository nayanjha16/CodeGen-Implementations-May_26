"""DesignPatternsSolid | kind=combo | label=observer+srp | domain=analytics | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AnalyticsObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class AnalyticsSubject:
    def __init__(self) -> None:
        self.observers: list[AnalyticsObserver] = []
        self.events: list[str] = []

    def attach(self, o: AnalyticsObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class AnalyticsListener(AnalyticsObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"analytics:{event}"
