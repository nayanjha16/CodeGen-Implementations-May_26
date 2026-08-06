"""DesignPatternsSolid | kind=design_pattern | label=decorator | domain=queue | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class QueueComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class QueueCore(QueueComponent):
    def process(self, input: str) -> str:
        return f"queue:{input}"

class QueueUpperDecorator(QueueComponent):
    def __init__(self, inner: QueueComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
