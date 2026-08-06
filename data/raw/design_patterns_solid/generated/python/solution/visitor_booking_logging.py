"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=booking | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BookingVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "BookingLeaf") -> str: ...

class BookingElement(ABC):
    @abstractmethod
    def accept(self, v: BookingVisitor) -> str: ...

class BookingLeaf(BookingElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: BookingVisitor) -> str:
        return v.visit_leaf(self)

class BookingPrintVisitor(BookingVisitor):
    def visit_leaf(self, leaf: BookingLeaf) -> str:
        return f"booking:{leaf.name}"
