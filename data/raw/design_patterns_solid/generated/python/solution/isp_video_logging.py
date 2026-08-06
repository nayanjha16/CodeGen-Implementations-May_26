"""DesignPatternsSolid | kind=solid | label=isp | domain=video | tier=logging"""
from __future__ import annotations

from typing import Protocol

class VideoReadable(Protocol):
    def read(self) -> str: ...

class VideoWritable(Protocol):
    def write(self, v: str) -> None: ...

class VideoStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"video:{v}"

def mirror(r: VideoReadable) -> str:
    return r.read()
