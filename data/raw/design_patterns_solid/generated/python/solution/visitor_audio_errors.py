"""DesignPatternsSolid | kind=design_pattern | label=visitor | domain=audio | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AudioVisitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "AudioLeaf") -> str: ...

class AudioElement(ABC):
    @abstractmethod
    def accept(self, v: AudioVisitor) -> str: ...

class AudioLeaf(AudioElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: AudioVisitor) -> str:
        return v.visit_leaf(self)

class AudioPrintVisitor(AudioVisitor):
    def visit_leaf(self, leaf: AudioLeaf) -> str:
        return f"audio:{leaf.name}"
