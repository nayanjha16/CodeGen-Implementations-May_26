"""DesignPatternsSolid | kind=solid | label=isp | domain=cache | tier=minimal"""
from __future__ import annotations

from typing import Protocol

class CacheReadable(Protocol):
    def read(self) -> str: ...

class CacheWritable(Protocol):
    def write(self, v: str) -> None: ...

class CacheStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"cache:{v}"

def mirror(r: CacheReadable) -> str:
    return r.read()
