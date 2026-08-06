"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=analytics | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AnalyticsVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "AnalyticsLeaf") -> str: ...

class AnalyticsElement(ABC):
    @abstractmethod
    def accept(self, v: AnalyticsVisitor) -> str: ...

class AnalyticsLeaf(AnalyticsElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: AnalyticsVisitor) -> str:
        return v.visit_leaf(self)

class AnalyticsPrintVisitor(AnalyticsVisitor):
    def visit_leaf(self, leaf: AnalyticsLeaf) -> str:
        return f"analytics:{leaf.name}"
