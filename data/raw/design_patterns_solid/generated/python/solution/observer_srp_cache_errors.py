"""DesignPatternsSolid | kind=combo | label=observer+srp | domain=cache | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CacheObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class CacheSubject:
    def __init__(self) -> None:
        self.observers: list[CacheObserver] = []
        self.events: list[str] = []

    def attach(self, o: CacheObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class CacheListener(CacheObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"cache:{event}"
