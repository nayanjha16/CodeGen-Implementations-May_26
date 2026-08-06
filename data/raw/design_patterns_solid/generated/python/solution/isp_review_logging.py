"""DesignPatternsSolid | kind=solid | label=isp | domain=review | tier=logging"""
from __future__ import annotations

from typing import Protocol

class ReviewReadable(Protocol):
    def read(self) -> str: ...

class ReviewWritable(Protocol):
    def write(self, v: str) -> None: ...

class ReviewStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"review:{v}"

def mirror(r: ReviewReadable) -> str:
    return r.read()
