"""DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=backup | tier=logging"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class BackupHandler(ABC):
    def __init__(self) -> None:
        self.next: BackupHandler | None = None

    def link(self, n: BackupHandler) -> BackupHandler:
        self.next = n
        return n

    def handle(self, level: int, msg: str) -> str:
        if self.can_handle(level):
            return self.do_handle(msg)
        if self.next is not None:
            return self.next.handle(level, msg)
        return "unhandled-backup"

    @abstractmethod
    def can_handle(self, level: int) -> bool: ...
    @abstractmethod
    def do_handle(self, msg: str) -> str: ...

class BackupLowHandler(BackupHandler):
    def can_handle(self, level: int) -> bool:
        return level <= 1
    def do_handle(self, msg: str) -> str:
        return f"low-backup:{msg}"

class BackupHighHandler(BackupHandler):
    def can_handle(self, level: int) -> bool:
        return level > 1
    def do_handle(self, msg: str) -> str:
        return f"high-backup:{msg}"
