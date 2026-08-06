"""DesignPatternsSolid | kind=solid | label=isp | domain=storage | tier=minimal"""
from __future__ import annotations

from typing import Protocol

class StorageReadable(Protocol):
    def read(self) -> str: ...

class StorageWritable(Protocol):
    def write(self, v: str) -> None: ...

class StorageStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"storage:{v}"

def mirror(r: StorageReadable) -> str:
    return r.read()
