"""DesignPatternsSolid | kind=combo | label=observer+srp | domain=streaming | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class StreamingObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class StreamingSubject:
    def __init__(self) -> None:
        self.observers: list[StreamingObserver] = []
        self.events: list[str] = []

    def attach(self, o: StreamingObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class StreamingListener(StreamingObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"streaming:{event}"
