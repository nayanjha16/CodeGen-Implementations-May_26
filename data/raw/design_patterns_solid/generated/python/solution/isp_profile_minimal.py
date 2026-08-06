"""DesignPatternsSolid | kind=solid | label=isp | domain=profile | tier=minimal"""
from __future__ import annotations

from typing import Protocol

class ProfileReadable(Protocol):
    def read(self) -> str: ...

class ProfileWritable(Protocol):
    def write(self, v: str) -> None: ...

class ProfileStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"profile:{v}"

def mirror(r: ProfileReadable) -> str:
    return r.read()
