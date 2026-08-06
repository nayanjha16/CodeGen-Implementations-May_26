"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=logging | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class LoggingComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class LoggingCore(LoggingComponent):
    def process(self, input: str) -> str:
        return f"logging:{input}"

class LoggingUpperDecorator(LoggingComponent):
    def __init__(self, inner: LoggingComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
