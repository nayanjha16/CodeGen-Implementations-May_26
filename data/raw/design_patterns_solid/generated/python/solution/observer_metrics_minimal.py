"""DesignPatternsSolid | kind=design_pattern | label=observer | domain=metrics | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MetricsObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class MetricsSubject:
    def __init__(self) -> None:
        self.observers: list[MetricsObserver] = []
        self.events: list[str] = []

    def attach(self, o: MetricsObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class MetricsListener(MetricsObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"metrics:{event}"
