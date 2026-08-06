"""DesignPatternsSolid | kind=combo | label=observer+srp | domain=inventory | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class InventoryObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class InventorySubject:
    def __init__(self) -> None:
        self.observers: list[InventoryObserver] = []
        self.events: list[str] = []

    def attach(self, o: InventoryObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class InventoryListener(InventoryObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"inventory:{event}"
