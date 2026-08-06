"""DesignPatternsSolid | kind=solid | label=isp | domain=booking | tier=minimal"""
from __future__ import annotations

from typing import Protocol

class BookingReadable(Protocol):
    def read(self) -> str: ...

class BookingWritable(Protocol):
    def write(self, v: str) -> None: ...

class BookingStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"booking:{v}"

def mirror(r: BookingReadable) -> str:
    return r.read()
