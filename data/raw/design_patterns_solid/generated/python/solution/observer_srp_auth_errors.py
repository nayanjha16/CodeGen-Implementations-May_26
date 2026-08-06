"""DesignPatternsSolid | kind=combo | label=observer+srp | domain=auth | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AuthObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class AuthSubject:
    def __init__(self) -> None:
        self.observers: list[AuthObserver] = []
        self.events: list[str] = []

    def attach(self, o: AuthObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class AuthListener(AuthObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"auth:{event}"
