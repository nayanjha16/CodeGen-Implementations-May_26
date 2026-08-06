"""DesignPatternsSolid | kind=combo | label=observer+srp | domain=game | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class GameObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class GameSubject:
    def __init__(self) -> None:
        self.observers: list[GameObserver] = []
        self.events: list[str] = []

    def attach(self, o: GameObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class GameListener(GameObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"game:{event}"
