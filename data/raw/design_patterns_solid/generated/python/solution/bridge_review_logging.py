"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=review | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ReviewImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class ReviewFileImpl(ReviewImpl):
    def write(self, msg: str) -> str:
        return f"file:review:{msg}"

class ReviewMemoryImpl(ReviewImpl):
    def write(self, msg: str) -> str:
        return f"mem:review:{msg}"

class ReviewBridge(ABC):
    def __init__(self, impl: ReviewImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class ReviewAlertBridge(ReviewBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
