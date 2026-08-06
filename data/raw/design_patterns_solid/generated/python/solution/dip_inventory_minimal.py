"""DesignPatternsSolid | kind=solid | label=dip | domain=inventory | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class InventoryGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class InventoryHttpGateway(InventoryGateway):
    def send(self, payload: str) -> str:
        return f"http-inventory:{payload}"

class InventoryAppService:
    def __init__(self, gateway: InventoryGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
