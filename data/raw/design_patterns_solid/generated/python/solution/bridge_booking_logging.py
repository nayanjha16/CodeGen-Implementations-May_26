"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=booking | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BookingImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class BookingFileImpl(BookingImpl):
    def write(self, msg: str) -> str:
        return f"file:booking:{msg}"

class BookingMemoryImpl(BookingImpl):
    def write(self, msg: str) -> str:
        return f"mem:booking:{msg}"

class BookingBridge(ABC):
    def __init__(self, impl: BookingImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class BookingAlertBridge(BookingBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
