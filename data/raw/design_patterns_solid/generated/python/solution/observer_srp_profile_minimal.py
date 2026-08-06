"""DesignPatternsSolid | kind=combo | label=observer+srp | domain=profile | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ProfileObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class ProfileSubject:
    def __init__(self) -> None:
        self.observers: list[ProfileObserver] = []
        self.events: list[str] = []

    def attach(self, o: ProfileObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class ProfileListener(ProfileObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"profile:{event}"
