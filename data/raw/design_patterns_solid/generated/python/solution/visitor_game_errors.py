"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=game | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class GameVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "GameLeaf") -> str: ...

class GameElement(ABC):
    @abstractmethod
    def accept(self, v: GameVisitor) -> str: ...

class GameLeaf(GameElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: GameVisitor) -> str:
        return v.visit_leaf(self)

class GamePrintVisitor(GameVisitor):
    def visit_leaf(self, leaf: GameLeaf) -> str:
        return f"game:{leaf.name}"
