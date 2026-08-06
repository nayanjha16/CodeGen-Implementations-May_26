"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=chat | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ChatProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class ChatBasicProduct(ChatProduct):
    def operate(self) -> str:
        return "basic-chat"

class ChatPremiumProduct(ChatProduct):
    def operate(self) -> str:
        return "premium-chat"

class ChatFactory:
    def create(self, type_name: str) -> ChatProduct:
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return ChatPremiumProduct()
        return ChatBasicProduct()
