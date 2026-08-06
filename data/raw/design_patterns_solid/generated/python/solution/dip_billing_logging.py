"""DesignPatternsSolid | kind=solid | label=dip | domain=billing | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BillingGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class BillingHttpGateway(BillingGateway):
    def send(self, payload: str) -> str:
        return f"http-billing:{payload}"

class BillingAppService:
    def __init__(self, gateway: BillingGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
