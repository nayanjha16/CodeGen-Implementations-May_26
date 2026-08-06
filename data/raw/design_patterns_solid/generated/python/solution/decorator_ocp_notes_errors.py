"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=notes | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class NotesComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class NotesCore(NotesComponent):
    def process(self, input: str) -> str:
        return f"notes:{input}"

class NotesUpperDecorator(NotesComponent):
    def __init__(self, inner: NotesComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
