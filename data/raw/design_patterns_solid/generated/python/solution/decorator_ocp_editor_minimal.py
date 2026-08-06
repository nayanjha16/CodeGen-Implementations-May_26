"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=editor | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class EditorComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class EditorCore(EditorComponent):
    def process(self, input: str) -> str:
        return f"editor:{input}"

class EditorUpperDecorator(EditorComponent):
    def __init__(self, inner: EditorComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
