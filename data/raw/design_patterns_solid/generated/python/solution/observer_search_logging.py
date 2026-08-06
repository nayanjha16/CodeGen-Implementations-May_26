"""DesignPatternsSolid | kind=design_pattern | label=observer | domain=search | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SearchObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class SearchSubject:
    def __init__(self) -> None:
        self.observers: list[SearchObserver] = []
        self.events: list[str] = []

    def attach(self, o: SearchObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class SearchListener(SearchObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"search:{event}"
