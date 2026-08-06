"""DesignPatternsSolid | kind=solid | label=isp | domain=audio | tier=errors"""
from __future__ import annotations

from typing import Protocol

class AudioReadable(Protocol):
    def read(self) -> str: ...

class AudioWritable(Protocol):
    def write(self, v: str) -> None: ...

class AudioStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"audio:{v}"

def mirror(r: AudioReadable) -> str:
    return r.read()
