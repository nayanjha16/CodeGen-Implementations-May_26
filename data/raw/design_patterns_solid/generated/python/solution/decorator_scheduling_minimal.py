"""DesignPatternsSolid | kind=design_pattern | label=decorator | domain=scheduling | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SchedulingComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class SchedulingCore(SchedulingComponent):
    def process(self, input: str) -> str:
        return f"scheduling:{input}"

class SchedulingUpperDecorator(SchedulingComponent):
    def __init__(self, inner: SchedulingComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
