"""DesignPatternsSolid | kind=solid | label=isp | domain=comment | tier=logging"""
from __future__ import annotations

from typing import Protocol

class CommentReadable(Protocol):
    def read(self) -> str: ...

class CommentWritable(Protocol):
    def write(self, v: str) -> None: ...

class CommentStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"comment:{v}"

def mirror(r: CommentReadable) -> str:
    return r.read()
