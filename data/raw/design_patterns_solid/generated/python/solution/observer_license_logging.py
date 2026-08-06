"""DesignPatternsSolid | kind=design_pattern | label=observer | domain=license | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class LicenseObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class LicenseSubject:
    def __init__(self) -> None:
        self.observers: list[LicenseObserver] = []
        self.events: list[str] = []

    def attach(self, o: LicenseObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class LicenseListener(LicenseObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"license:{event}"
