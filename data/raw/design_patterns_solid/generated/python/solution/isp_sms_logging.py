"""DesignPatternsSolid | kind=solid | label=isp | domain=sms | tier=logging"""
from __future__ import annotations

from typing import Protocol

class SmsReadable(Protocol):
    def read(self) -> str: ...

class SmsWritable(Protocol):
    def write(self, v: str) -> None: ...

class SmsStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"sms:{v}"

def mirror(r: SmsReadable) -> str:
    return r.read()
