"""DesignPatternsSolid | kind=design_pattern | label=observer | domain=database | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DatabaseObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class DatabaseSubject:
    def __init__(self) -> None:
        self.observers: list[DatabaseObserver] = []
        self.events: list[str] = []

    def attach(self, o: DatabaseObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class DatabaseListener(DatabaseObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"database:{event}"
