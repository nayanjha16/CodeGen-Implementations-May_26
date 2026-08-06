"""DesignPatternsSolid | kind=solid | label=isp | domain=auth | tier=errors"""
from __future__ import annotations

from typing import Protocol

class AuthReadable(Protocol):
    def read(self) -> str: ...

class AuthWritable(Protocol):
    def write(self, v: str) -> None: ...

class AuthStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"auth:{v}"

def mirror(r: AuthReadable) -> str:
    return r.read()
