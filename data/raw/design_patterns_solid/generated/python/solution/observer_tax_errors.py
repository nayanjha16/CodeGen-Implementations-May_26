"""DesignPatternsSolid | kind=design_pattern | label=observer | domain=tax | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TaxObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class TaxSubject:
    def __init__(self) -> None:
        self.observers: list[TaxObserver] = []
        self.events: list[str] = []

    def attach(self, o: TaxObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class TaxListener(TaxObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"tax:{event}"
