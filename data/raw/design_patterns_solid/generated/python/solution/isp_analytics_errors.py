"""DesignPatternsSolid | kind=solid | label=isp | domain=analytics | tier=errors"""
from __future__ import annotations

from typing import Protocol

class AnalyticsReadable(Protocol):
    def read(self) -> str: ...

class AnalyticsWritable(Protocol):
    def write(self, v: str) -> None: ...

class AnalyticsStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"analytics:{v}"

def mirror(r: AnalyticsReadable) -> str:
    return r.read()
