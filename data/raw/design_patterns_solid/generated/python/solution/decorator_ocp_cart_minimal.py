"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=cart | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CartComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class CartCore(CartComponent):
    def process(self, input: str) -> str:
        return f"cart:{input}"

class CartUpperDecorator(CartComponent):
    def __init__(self, inner: CartComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
