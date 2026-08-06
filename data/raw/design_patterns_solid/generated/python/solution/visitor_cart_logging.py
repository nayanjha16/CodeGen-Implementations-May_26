"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=cart | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CartVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "CartLeaf") -> str: ...

class CartElement(ABC):
    @abstractmethod
    def accept(self, v: CartVisitor) -> str: ...

class CartLeaf(CartElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: CartVisitor) -> str:
        return v.visit_leaf(self)

class CartPrintVisitor(CartVisitor):
    def visit_leaf(self, leaf: CartLeaf) -> str:
        return f"cart:{leaf.name}"
