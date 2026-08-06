"""DesignPatternsSolid | kind=design_pattern | label=decorator | domain=shipping | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ShippingComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class ShippingCore(ShippingComponent):
    def process(self, input: str) -> str:
        return f"shipping:{input}"

class ShippingUpperDecorator(ShippingComponent):
    def __init__(self, inner: ShippingComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
