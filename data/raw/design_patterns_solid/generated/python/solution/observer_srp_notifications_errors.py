"""DesignPatternsSolid | kind=combo | label=observer+srp | domain=notifications | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class NotificationsObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class NotificationsSubject:
    def __init__(self) -> None:
        self.observers: list[NotificationsObserver] = []
        self.events: list[str] = []

    def attach(self, o: NotificationsObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class NotificationsListener(NotificationsObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"notifications:{event}"
