"""DesignPatternsSolid | kind=solid | label=isp | domain=metrics | tier=minimal"""
from __future__ import annotations

from typing import Protocol

class MetricsReadable(Protocol):
    def read(self) -> str: ...

class MetricsWritable(Protocol):
    def write(self, v: str) -> None: ...

class MetricsStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"metrics:{v}"

def mirror(r: MetricsReadable) -> str:
    return r.read()
