"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=comment | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CommentComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class CommentCore(CommentComponent):
    def process(self, input: str) -> str:
        return f"comment:{input}"

class CommentUpperDecorator(CommentComponent):
    def __init__(self, inner: CommentComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
