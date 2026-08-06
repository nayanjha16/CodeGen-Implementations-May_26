"""DesignPatternsSolid | kind=combo | label=observer+srp | domain=scheduling | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SchedulingObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class SchedulingSubject:
    def __init__(self) -> None:
        self.observers: list[SchedulingObserver] = []
        self.events: list[str] = []

    def attach(self, o: SchedulingObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class SchedulingListener(SchedulingObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"scheduling:{event}"
