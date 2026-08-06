"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=chat | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ChatVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "ChatLeaf") -> str: ...

class ChatElement(ABC):
    @abstractmethod
    def accept(self, v: ChatVisitor) -> str: ...

class ChatLeaf(ChatElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: ChatVisitor) -> str:
        return v.visit_leaf(self)

class ChatPrintVisitor(ChatVisitor):
    def visit_leaf(self, leaf: ChatLeaf) -> str:
        return f"chat:{leaf.name}"
