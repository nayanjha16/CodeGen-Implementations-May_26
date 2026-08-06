"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=canvas | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CanvasVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "CanvasLeaf") -> str: ...

class CanvasElement(ABC):
    @abstractmethod
    def accept(self, v: CanvasVisitor) -> str: ...

class CanvasLeaf(CanvasElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: CanvasVisitor) -> str:
        return v.visit_leaf(self)

class CanvasPrintVisitor(CanvasVisitor):
    def visit_leaf(self, leaf: CanvasLeaf) -> str:
        return f"canvas:{leaf.name}"
