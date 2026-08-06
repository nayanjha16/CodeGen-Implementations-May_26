"""DesignPatternsSolid | kind=combo | label=observer+srp | domain=storage | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class StorageObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class StorageSubject:
    def __init__(self) -> None:
        self.observers: list[StorageObserver] = []
        self.events: list[str] = []

    def attach(self, o: StorageObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class StorageListener(StorageObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"storage:{event}"
