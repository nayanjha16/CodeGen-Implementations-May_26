"""DesignPatternsSolid | kind=solid | label=isp | domain=calendar | tier=logging"""
from __future__ import annotations

from typing import Protocol

class CalendarReadable(Protocol):
    def read(self) -> str: ...

class CalendarWritable(Protocol):
    def write(self, v: str) -> None: ...

class CalendarStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"calendar:{v}"

def mirror(r: CalendarReadable) -> str:
    return r.read()
