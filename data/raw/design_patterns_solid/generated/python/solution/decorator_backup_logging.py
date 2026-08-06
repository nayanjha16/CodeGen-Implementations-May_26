"""DesignPatternsSolid | kind=design_pattern | label=decorator | domain=backup | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BackupComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class BackupCore(BackupComponent):
    def process(self, input: str) -> str:
        return f"backup:{input}"

class BackupUpperDecorator(BackupComponent):
    def __init__(self, inner: BackupComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
