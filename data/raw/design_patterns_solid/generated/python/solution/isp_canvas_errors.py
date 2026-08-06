"""DesignPatternsSolid | kind=solid | label=isp | domain=canvas | tier=errors"""
from __future__ import annotations

from typing import Protocol

class CanvasReadable(Protocol):
    def read(self) -> str: ...

class CanvasWritable(Protocol):
    def write(self, v: str) -> None: ...

class CanvasStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"canvas:{v}"

def mirror(r: CanvasReadable) -> str:
    return r.read()
