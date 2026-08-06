"""DesignPatternsSolid | kind=design_pattern | label=decorator | domain=email | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class EmailComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class EmailCore(EmailComponent):
    def process(self, input: str) -> str:
        return f"email:{input}"

class EmailUpperDecorator(EmailComponent):
    def __init__(self, inner: EmailComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
