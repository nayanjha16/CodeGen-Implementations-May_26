"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=session | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SessionComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class SessionCore(SessionComponent):
    def process(self, input: str) -> str:
        return f"session:{input}"

class SessionUpperDecorator(SessionComponent):
    def __init__(self, inner: SessionComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
