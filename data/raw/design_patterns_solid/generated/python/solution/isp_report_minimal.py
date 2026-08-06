"""DesignPatternsSolid | kind=solid | label=isp | domain=report | tier=minimal"""
from __future__ import annotations

from typing import Protocol

class ReportReadable(Protocol):
    def read(self) -> str: ...

class ReportWritable(Protocol):
    def write(self, v: str) -> None: ...

class ReportStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"report:{v}"

def mirror(r: ReportReadable) -> str:
    return r.read()
