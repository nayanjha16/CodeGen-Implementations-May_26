"""DesignPatternsSolid | kind=solid | label=isp | domain=session | tier=minimal"""
from __future__ import annotations

from typing import Protocol

class SessionReadable(Protocol):
    def read(self) -> str: ...

class SessionWritable(Protocol):
    def write(self, v: str) -> None: ...

class SessionStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"session:{v}"

def mirror(r: SessionReadable) -> str:
    return r.read()
