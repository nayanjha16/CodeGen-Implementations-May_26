"""DesignPatternsSolid | kind=design_pattern | label=decorator | domain=chat | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ChatComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class ChatCore(ChatComponent):
    def process(self, input: str) -> str:
        return f"chat:{input}"

class ChatUpperDecorator(ChatComponent):
    def __init__(self, inner: ChatComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
