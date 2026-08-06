"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=cart | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CartService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class CartRealService(CartService):
    def load(self, id: str) -> str:
        return f"real-cart:{id}"

class CartProxy(CartService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: CartRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = CartRealService()
        return self._real.load(id)
