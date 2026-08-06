"""DesignPatternsSolid | kind=design_pattern | label=observer | domain=session | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SessionObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class SessionSubject:
    def __init__(self) -> None:
        self.observers: list[SessionObserver] = []
        self.events: list[str] = []

    def attach(self, o: SessionObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class SessionListener(SessionObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"session:{event}"
