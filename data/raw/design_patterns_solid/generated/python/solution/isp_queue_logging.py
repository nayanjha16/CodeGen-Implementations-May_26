"""DesignPatternsSolid | kind=solid | label=isp | domain=queue | tier=logging"""
from __future__ import annotations

from typing import Protocol

class QueueReadable(Protocol):
    def read(self) -> str: ...

class QueueWritable(Protocol):
    def write(self, v: str) -> None: ...

class QueueStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"queue:{v}"

def mirror(r: QueueReadable) -> str:
    return r.read()
