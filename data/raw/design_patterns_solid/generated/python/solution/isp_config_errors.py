"""DesignPatternsSolid | kind=solid | label=isp | domain=config | tier=errors"""
from __future__ import annotations

from typing import Protocol

class ConfigReadable(Protocol):
    def read(self) -> str: ...

class ConfigWritable(Protocol):
    def write(self, v: str) -> None: ...

class ConfigStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"config:{v}"

def mirror(r: ConfigReadable) -> str:
    return r.read()
