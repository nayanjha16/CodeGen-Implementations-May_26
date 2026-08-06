"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=profile | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ProfileVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "ProfileLeaf") -> str: ...

class ProfileElement(ABC):
    @abstractmethod
    def accept(self, v: ProfileVisitor) -> str: ...

class ProfileLeaf(ProfileElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: ProfileVisitor) -> str:
        return v.visit_leaf(self)

class ProfilePrintVisitor(ProfileVisitor):
    def visit_leaf(self, leaf: ProfileLeaf) -> str:
        return f"profile:{leaf.name}"
