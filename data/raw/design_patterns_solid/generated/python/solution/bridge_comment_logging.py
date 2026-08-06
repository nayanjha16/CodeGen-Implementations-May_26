"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=comment | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CommentImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class CommentFileImpl(CommentImpl):
    def write(self, msg: str) -> str:
        return f"file:comment:{msg}"

class CommentMemoryImpl(CommentImpl):
    def write(self, msg: str) -> str:
        return f"mem:comment:{msg}"

class CommentBridge(ABC):
    def __init__(self, impl: CommentImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class CommentAlertBridge(CommentBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
