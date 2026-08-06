"""DesignPatternsSolid | kind=solid | label=isp | domain=notifications | tier=errors"""
from __future__ import annotations

from typing import Protocol

class NotificationsReadable(Protocol):
    def read(self) -> str: ...

class NotificationsWritable(Protocol):
    def write(self, v: str) -> None: ...

class NotificationsStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"notifications:{v}"

def mirror(r: NotificationsReadable) -> str:
    return r.read()
