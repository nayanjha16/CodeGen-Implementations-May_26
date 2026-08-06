"""DesignPatternsSolid | kind=solid | label=isp | domain=map | tier=minimal"""
from __future__ import annotations

from typing import Protocol

class MapReadable(Protocol):
    def read(self) -> str: ...

class MapWritable(Protocol):
    def write(self, v: str) -> None: ...

class MapStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"map:{v}"

def mirror(r: MapReadable) -> str:
    return r.read()
