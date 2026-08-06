"""DesignPatternsSolid | kind=solid | label=isp | domain=notes | tier=errors"""
from __future__ import annotations

from typing import Protocol

class NotesReadable(Protocol):
    def read(self) -> str: ...

class NotesWritable(Protocol):
    def write(self, v: str) -> None: ...

class NotesStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"notes:{v}"

def mirror(r: NotesReadable) -> str:
    return r.read()
