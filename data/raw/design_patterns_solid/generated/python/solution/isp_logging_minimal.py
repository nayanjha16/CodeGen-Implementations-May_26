"""DesignPatternsSolid | kind=solid | label=isp | domain=logging | tier=minimal"""
from __future__ import annotations

from typing import Protocol

class LoggingReadable(Protocol):
    def read(self) -> str: ...

class LoggingWritable(Protocol):
    def write(self, v: str) -> None: ...

class LoggingStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"logging:{v}"

def mirror(r: LoggingReadable) -> str:
    return r.read()
