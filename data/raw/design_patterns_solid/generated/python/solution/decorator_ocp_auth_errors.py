"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=auth | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AuthComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class AuthCore(AuthComponent):
    def process(self, input: str) -> str:
        return f"auth:{input}"

class AuthUpperDecorator(AuthComponent):
    def __init__(self, inner: AuthComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
