"""DesignPatternsSolid | kind=solid | label=dip | domain=canvas | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CanvasGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class CanvasHttpGateway(CanvasGateway):
    def send(self, payload: str) -> str:
        return f"http-canvas:{payload}"

class CanvasAppService:
    def __init__(self, gateway: CanvasGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
