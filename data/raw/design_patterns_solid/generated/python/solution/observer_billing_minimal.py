"""DesignPatternsSolid | kind=design_pattern | label=observer | domain=billing | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BillingObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class BillingSubject:
    def __init__(self) -> None:
        self.observers: list[BillingObserver] = []
        self.events: list[str] = []

    def attach(self, o: BillingObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class BillingListener(BillingObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"billing:{event}"
