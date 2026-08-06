"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=sensors | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SensorsVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "SensorsLeaf") -> str: ...

class SensorsElement(ABC):
    @abstractmethod
    def accept(self, v: SensorsVisitor) -> str: ...

class SensorsLeaf(SensorsElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: SensorsVisitor) -> str:
        return v.visit_leaf(self)

class SensorsPrintVisitor(SensorsVisitor):
    def visit_leaf(self, leaf: SensorsLeaf) -> str:
        return f"sensors:{leaf.name}"
