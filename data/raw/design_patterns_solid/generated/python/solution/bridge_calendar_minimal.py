"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=calendar | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CalendarImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class CalendarFileImpl(CalendarImpl):
    def write(self, msg: str) -> str:
        return f"file:calendar:{msg}"

class CalendarMemoryImpl(CalendarImpl):
    def write(self, msg: str) -> str:
        return f"mem:calendar:{msg}"

class CalendarBridge(ABC):
    def __init__(self, impl: CalendarImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class CalendarAlertBridge(CalendarBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
