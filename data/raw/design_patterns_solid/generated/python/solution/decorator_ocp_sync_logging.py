"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=sync | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SyncComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class SyncCore(SyncComponent):
    def process(self, input: str) -> str:
        return f"sync:{input}"

class SyncUpperDecorator(SyncComponent):
    def __init__(self, inner: SyncComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
