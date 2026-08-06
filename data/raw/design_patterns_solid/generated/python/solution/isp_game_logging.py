"""DesignPatternsSolid | kind=solid | label=isp | domain=game | tier=logging"""
from __future__ import annotations

from typing import Protocol

class GameReadable(Protocol):
    def read(self) -> str: ...

class GameWritable(Protocol):
    def write(self, v: str) -> None: ...

class GameStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"game:{v}"

def mirror(r: GameReadable) -> str:
    return r.read()
