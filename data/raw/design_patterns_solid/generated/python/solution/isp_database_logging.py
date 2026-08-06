"""DesignPatternsSolid | kind=solid | label=isp | domain=database | tier=logging"""
from __future__ import annotations

from typing import Protocol

class DatabaseReadable(Protocol):
    def read(self) -> str: ...

class DatabaseWritable(Protocol):
    def write(self, v: str) -> None: ...

class DatabaseStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"database:{v}"

def mirror(r: DatabaseReadable) -> str:
    return r.read()
