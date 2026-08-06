"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=map | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MapVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "MapLeaf") -> str: ...

class MapElement(ABC):
    @abstractmethod
    def accept(self, v: MapVisitor) -> str: ...

class MapLeaf(MapElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: MapVisitor) -> str:
        return v.visit_leaf(self)

class MapPrintVisitor(MapVisitor):
    def visit_leaf(self, leaf: MapLeaf) -> str:
        return f"map:{leaf.name}"
