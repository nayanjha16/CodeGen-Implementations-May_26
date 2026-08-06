"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=billing | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BillingVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "BillingLeaf") -> str: ...

class BillingElement(ABC):
    @abstractmethod
    def accept(self, v: BillingVisitor) -> str: ...

class BillingLeaf(BillingElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: BillingVisitor) -> str:
        return v.visit_leaf(self)

class BillingPrintVisitor(BillingVisitor):
    def visit_leaf(self, leaf: BillingLeaf) -> str:
        return f"billing:{leaf.name}"
