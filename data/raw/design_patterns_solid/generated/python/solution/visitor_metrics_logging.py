"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=metrics | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MetricsVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "MetricsLeaf") -> str: ...

class MetricsElement(ABC):
    @abstractmethod
    def accept(self, v: MetricsVisitor) -> str: ...

class MetricsLeaf(MetricsElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: MetricsVisitor) -> str:
        return v.visit_leaf(self)

class MetricsPrintVisitor(MetricsVisitor):
    def visit_leaf(self, leaf: MetricsLeaf) -> str:
        return f"metrics:{leaf.name}"
