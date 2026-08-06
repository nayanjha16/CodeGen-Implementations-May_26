"""DesignPatternsSolid | kind=design_pattern | label=decorator | domain=discount | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DiscountComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class DiscountCore(DiscountComponent):
    def process(self, input: str) -> str:
        return f"discount:{input}"

class DiscountUpperDecorator(DiscountComponent):
    def __init__(self, inner: DiscountComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
