"""DesignPatternsSolid | kind=design_pattern | label=observer | domain=todo | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TodoObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class TodoSubject:
    def __init__(self) -> None:
        self.observers: list[TodoObserver] = []
        self.events: list[str] = []

    def attach(self, o: TodoObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class TodoListener(TodoObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"todo:{event}"
