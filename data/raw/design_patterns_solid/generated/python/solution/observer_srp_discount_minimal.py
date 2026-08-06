"""DesignPatternsSolid | kind=combo | label=observer+srp | domain=discount | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DiscountObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class DiscountSubject:
    def __init__(self) -> None:
        self.observers: list[DiscountObserver] = []
        self.events: list[str] = []

    def attach(self, o: DiscountObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class DiscountListener(DiscountObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"discount:{event}"
