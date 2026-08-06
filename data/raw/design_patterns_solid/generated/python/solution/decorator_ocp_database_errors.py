"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=database | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DatabaseComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class DatabaseCore(DatabaseComponent):
    def process(self, input: str) -> str:
        return f"database:{input}"

class DatabaseUpperDecorator(DatabaseComponent):
    def __init__(self, inner: DatabaseComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
