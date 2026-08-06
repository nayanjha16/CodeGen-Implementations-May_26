"""DesignPatternsSolid | kind=solid | label=isp | domain=email | tier=logging"""
from __future__ import annotations

from typing import Protocol

class EmailReadable(Protocol):
    def read(self) -> str: ...

class EmailWritable(Protocol):
    def write(self, v: str) -> None: ...

class EmailStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"email:{v}"

def mirror(r: EmailReadable) -> str:
    return r.read()
