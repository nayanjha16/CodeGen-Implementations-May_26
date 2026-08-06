"""DesignPatternsSolid | kind=solid | label=dip | domain=payments | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PaymentsGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class PaymentsHttpGateway(PaymentsGateway):
    def send(self, payload: str) -> str:
        return f"http-payments:{payload}"

class PaymentsAppService:
    def __init__(self, gateway: PaymentsGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
