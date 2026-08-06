"""DesignPatternsSolid | kind=combo | label=observer+srp | domain=video | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class VideoObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class VideoSubject:
    def __init__(self) -> None:
        self.observers: list[VideoObserver] = []
        self.events: list[str] = []

    def attach(self, o: VideoObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class VideoListener(VideoObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"video:{event}"
