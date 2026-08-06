"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=chat | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ChatService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class ChatRealService(ChatService):
    def load(self, id: str) -> str:
        return f"real-chat:{id}"

class ChatProxy(ChatService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: ChatRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = ChatRealService()
        return self._real.load(id)
