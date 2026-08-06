"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=chat | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ChatImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class ChatFileImpl(ChatImpl):
    def write(self, msg: str) -> str:
        return f"file:chat:{msg}"

class ChatMemoryImpl(ChatImpl):
    def write(self, msg: str) -> str:
        return f"mem:chat:{msg}"

class ChatBridge(ABC):
    def __init__(self, impl: ChatImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class ChatAlertBridge(ChatBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
