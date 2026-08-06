"""DesignPatternsSolid | kind=solid | label=isp | domain=scheduling | tier=errors"""
from __future__ import annotations

from typing import Protocol

class SchedulingReadable(Protocol):
    def read(self) -> str: ...

class SchedulingWritable(Protocol):
    def write(self, v: str) -> None: ...

class SchedulingStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"scheduling:{v}"

def mirror(r: SchedulingReadable) -> str:
    return r.read()
