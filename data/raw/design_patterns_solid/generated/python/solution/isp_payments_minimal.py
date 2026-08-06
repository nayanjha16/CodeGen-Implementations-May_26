"""DesignPatternsSolid | kind=solid | label=isp | domain=payments | tier=minimal"""
from __future__ import annotations

from typing import Protocol

class PaymentsReadable(Protocol):
    def read(self) -> str: ...

class PaymentsWritable(Protocol):
    def write(self, v: str) -> None: ...

class PaymentsStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"payments:{v}"

def mirror(r: PaymentsReadable) -> str:
    return r.read()
