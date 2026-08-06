"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=tax | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TaxComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class TaxCore(TaxComponent):
    def process(self, input: str) -> str:
        return f"tax:{input}"

class TaxUpperDecorator(TaxComponent):
    def __init__(self, inner: TaxComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
