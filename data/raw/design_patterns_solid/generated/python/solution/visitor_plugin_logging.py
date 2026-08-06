"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=plugin | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PluginVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "PluginLeaf") -> str: ...

class PluginElement(ABC):
    @abstractmethod
    def accept(self, v: PluginVisitor) -> str: ...

class PluginLeaf(PluginElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: PluginVisitor) -> str:
        return v.visit_leaf(self)

class PluginPrintVisitor(PluginVisitor):
    def visit_leaf(self, leaf: PluginLeaf) -> str:
        return f"plugin:{leaf.name}"
