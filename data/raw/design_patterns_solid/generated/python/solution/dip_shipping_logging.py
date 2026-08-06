"""DesignPatternsSolid | kind=solid | label=dip | domain=shipping | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ShippingGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class ShippingHttpGateway(ShippingGateway):
    def send(self, payload: str) -> str:
        return f"http-shipping:{payload}"

class ShippingAppService:
    def __init__(self, gateway: ShippingGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
