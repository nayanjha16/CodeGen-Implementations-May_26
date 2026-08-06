"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=payments | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PaymentsVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "PaymentsLeaf") -> str: ...

class PaymentsElement(ABC):
    @abstractmethod
    def accept(self, v: PaymentsVisitor) -> str: ...

class PaymentsLeaf(PaymentsElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: PaymentsVisitor) -> str:
        return v.visit_leaf(self)

class PaymentsPrintVisitor(PaymentsVisitor):
    def visit_leaf(self, leaf: PaymentsLeaf) -> str:
        return f"payments:{leaf.name}"
