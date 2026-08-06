"""DesignPatternsSolid | kind=solid | label=isp | domain=plugin | tier=minimal"""
from __future__ import annotations

from typing import Protocol

class PluginReadable(Protocol):
    def read(self) -> str: ...

class PluginWritable(Protocol):
    def write(self, v: str) -> None: ...

class PluginStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"plugin:{v}"

def mirror(r: PluginReadable) -> str:
    return r.read()
