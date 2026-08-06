"""DesignPatternsSolid | kind=combo | label=observer+srp | domain=cart | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CartObserver(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class CartSubject:
    def __init__(self) -> None:
        self.observers: list[CartObserver] = []
        self.events: list[str] = []

    def attach(self, o: CartObserver) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class CartListener(CartObserver):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"cart:{event}"
