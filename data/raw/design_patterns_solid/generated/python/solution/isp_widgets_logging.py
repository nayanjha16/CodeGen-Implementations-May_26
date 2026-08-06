"""DesignPatternsSolid | kind=solid | label=isp | domain=widgets | tier=logging"""
from __future__ import annotations

from typing import Protocol

class WidgetsReadable(Protocol):
    def read(self) -> str: ...

class WidgetsWritable(Protocol):
    def write(self, v: str) -> None: ...

class WidgetsStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"widgets:{v}"

def mirror(r: WidgetsReadable) -> str:
    return r.read()
