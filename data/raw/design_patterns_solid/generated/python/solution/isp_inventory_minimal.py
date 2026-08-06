"""DesignPatternsSolid | kind=solid | label=isp | domain=inventory | tier=minimal"""
from __future__ import annotations

from typing import Protocol

class InventoryReadable(Protocol):
    def read(self) -> str: ...

class InventoryWritable(Protocol):
    def write(self, v: str) -> None: ...

class InventoryStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"inventory:{v}"

def mirror(r: InventoryReadable) -> str:
    return r.read()
