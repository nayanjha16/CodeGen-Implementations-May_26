"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=video | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class VideoVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "VideoLeaf") -> str: ...

class VideoElement(ABC):
    @abstractmethod
    def accept(self, v: VideoVisitor) -> str: ...

class VideoLeaf(VideoElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: VideoVisitor) -> str:
        return v.visit_leaf(self)

class VideoPrintVisitor(VideoVisitor):
    def visit_leaf(self, leaf: VideoLeaf) -> str:
        return f"video:{leaf.name}"
