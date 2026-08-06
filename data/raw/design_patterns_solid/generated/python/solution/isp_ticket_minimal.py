"""DesignPatternsSolid | kind=solid | label=isp | domain=ticket | tier=minimal"""
from __future__ import annotations

from typing import Protocol

class TicketReadable(Protocol):
    def read(self) -> str: ...

class TicketWritable(Protocol):
    def write(self, v: str) -> None: ...

class TicketStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"ticket:{v}"

def mirror(r: TicketReadable) -> str:
    return r.read()
