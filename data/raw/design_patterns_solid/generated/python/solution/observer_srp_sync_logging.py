"""DesignPatternsSolid | kind=combo | label=observer+srp | domain=sync | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SyncObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class SyncSubject:
    def __init__(self) -> None:
        self.observers: list[SyncObserver] = []
        self.events: list[str] = []

    def attach(self, o: SyncObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class SyncListener(SyncObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"sync:{event}"
