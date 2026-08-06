"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=sensors | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SensorsComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class SensorsCore(SensorsComponent):
    def process(self, input: str) -> str:
        return f"sensors:{input}"

class SensorsUpperDecorator(SensorsComponent):
    def __init__(self, inner: SensorsComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
