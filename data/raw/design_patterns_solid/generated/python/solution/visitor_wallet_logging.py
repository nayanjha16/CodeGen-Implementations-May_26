"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=wallet | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WalletVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "WalletLeaf") -> str: ...

class WalletElement(ABC):
    @abstractmethod
    def accept(self, v: WalletVisitor) -> str: ...

class WalletLeaf(WalletElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: WalletVisitor) -> str:
        return v.visit_leaf(self)

class WalletPrintVisitor(WalletVisitor):
    def visit_leaf(self, leaf: WalletLeaf) -> str:
        return f"wallet:{leaf.name}"
