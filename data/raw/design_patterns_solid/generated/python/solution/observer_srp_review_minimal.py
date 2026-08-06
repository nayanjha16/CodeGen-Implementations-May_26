"""DesignPatternsSolid | kind=combo | label=observer+srp | domain=review | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ReviewObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class ReviewSubject:
    def __init__(self) -> None:
        self.observers: list[ReviewObserver] = []
        self.events: list[str] = []

    def attach(self, o: ReviewObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class ReviewListener(ReviewObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"review:{event}"
