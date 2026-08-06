"""DesignPatternsSolid | kind=solid | label=dip | domain=widgets | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WidgetsGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class WidgetsHttpGateway(WidgetsGateway):
    def send(self, payload: str) -> str:
        return f"http-widgets:{payload}"

class WidgetsAppService:
    def __init__(self, gateway: WidgetsGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
