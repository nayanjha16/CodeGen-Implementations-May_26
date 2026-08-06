"""DesignPatternsSolid | kind=solid | label=isp | domain=tax | tier=minimal"""
from __future__ import annotations

from typing import Protocol

class TaxReadable(Protocol):
    def read(self) -> str: ...

class TaxWritable(Protocol):
    def write(self, v: str) -> None: ...

class TaxStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"tax:{v}"

def mirror(r: TaxReadable) -> str:
    return r.read()
