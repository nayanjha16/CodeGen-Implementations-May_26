"""DesignPatternsSolid | kind=design_pattern | label=observer | domain=map | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MapObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class MapSubject:
    def __init__(self) -> None:
        self.observers: list[MapObserver] = []
        self.events: list[str] = []

    def attach(self, o: MapObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class MapListener(MapObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"map:{event}"
