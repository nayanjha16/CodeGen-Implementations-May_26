"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=storage | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class StorageVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "StorageLeaf") -> str: ...

class StorageElement(ABC):
    @abstractmethod
    def accept(self, v: StorageVisitor) -> str: ...

class StorageLeaf(StorageElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: StorageVisitor) -> str:
        return v.visit_leaf(self)

class StoragePrintVisitor(StorageVisitor):
    def visit_leaf(self, leaf: StorageLeaf) -> str:
        return f"storage:{leaf.name}"
