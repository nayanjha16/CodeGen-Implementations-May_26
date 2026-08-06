"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=ticket | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TicketImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class TicketFileImpl(TicketImpl):
    def write(self, msg: str) -> str:
        return f"file:ticket:{msg}"

class TicketMemoryImpl(TicketImpl):
    def write(self, msg: str) -> str:
        return f"mem:ticket:{msg}"

class TicketBridge(ABC):
    def __init__(self, impl: TicketImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class TicketAlertBridge(TicketBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
