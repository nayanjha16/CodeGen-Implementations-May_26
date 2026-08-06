"""DesignPatternsSolid | kind=solid | label=dip | domain=cart | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CartGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class CartHttpGateway(CartGateway):
    def send(self, payload: str) -> str:
        return f"http-cart:{payload}"

class CartAppService:
    def __init__(self, gateway: CartGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
