"""DesignPatternsSolid | kind=solid | label=isp | domain=discount | tier=logging"""
from __future__ import annotations

from typing import Protocol

class DiscountReadable(Protocol):
    def read(self) -> str: ...

class DiscountWritable(Protocol):
    def write(self, v: str) -> None: ...

class DiscountStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"discount:{v}"

def mirror(r: DiscountReadable) -> str:
    return r.read()
