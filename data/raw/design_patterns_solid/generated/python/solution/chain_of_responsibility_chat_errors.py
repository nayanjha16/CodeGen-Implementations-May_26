"""DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=chat | tier=errors"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class ChatHandler(ABC):
    def __init__(self) -> None:
        self.next: ChatHandler | None = None

    def link(self, n: ChatHandler) -> ChatHandler:
        self.next = n
        return n

    def handle(self, level: int, msg: str) -> str:
        if self.can_handle(level):
            return self.do_handle(msg)
        if self.next is not None:
            return self.next.handle(level, msg)
        return "unhandled-chat"

    @abstractmethod
    def can_handle(self, level: int) -> bool: ...
    @abstractmethod
    def do_handle(self, msg: str) -> str: ...

class ChatLowHandler(ChatHandler):
    def can_handle(self, level: int) -> bool:
        return level <= 1
    def do_handle(self, msg: str) -> str:
        return f"low-chat:{msg}"

class ChatHighHandler(ChatHandler):
    def can_handle(self, level: int) -> bool:
        return level > 1
    def do_handle(self, msg: str) -> str:
        return f"high-chat:{msg}"
