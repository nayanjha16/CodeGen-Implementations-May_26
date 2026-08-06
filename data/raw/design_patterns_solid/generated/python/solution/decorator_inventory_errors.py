"""DesignPatternsSolid | kind=design_pattern | label=decorator | domain=inventory | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class InventoryComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class InventoryCore(InventoryComponent):
    def process(self, input: str) -> str:
        return f"inventory:{input}"

class InventoryUpperDecorator(InventoryComponent):
    def __init__(self, inner: InventoryComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
