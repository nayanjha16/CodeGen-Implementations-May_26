"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=feed | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class FeedComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class FeedCore(FeedComponent):
    def process(self, input: str) -> str:
        return f"feed:{input}"

class FeedUpperDecorator(FeedComponent):
    def __init__(self, inner: FeedComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
