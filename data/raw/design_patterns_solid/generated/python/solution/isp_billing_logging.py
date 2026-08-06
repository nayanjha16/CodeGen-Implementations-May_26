"""DesignPatternsSolid | kind=solid | label=isp | domain=billing | tier=logging"""
from __future__ import annotations

from typing import Protocol

class BillingReadable(Protocol):
    def read(self) -> str: ...

class BillingWritable(Protocol):
    def write(self, v: str) -> None: ...

class BillingStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"billing:{v}"

def mirror(r: BillingReadable) -> str:
    return r.read()
