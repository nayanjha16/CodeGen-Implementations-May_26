"""DesignPatternsSolid | kind=solid | label=isp | domain=http | tier=logging"""
from __future__ import annotations

from typing import Protocol

class HttpReadable(Protocol):
    def read(self) -> str: ...

class HttpWritable(Protocol):
    def write(self, v: str) -> None: ...

class HttpStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"http:{v}"

def mirror(r: HttpReadable) -> str:
    return r.read()
