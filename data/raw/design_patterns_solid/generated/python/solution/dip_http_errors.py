"""DesignPatternsSolid | kind=solid | label=dip | domain=http | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class HttpGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class HttpHttpGateway(HttpGateway):
    def send(self, payload: str) -> str:
        return f"http-http:{payload}"

class HttpAppService:
    def __init__(self, gateway: HttpGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
