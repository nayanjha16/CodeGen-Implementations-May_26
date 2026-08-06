"""DesignPatternsSolid | kind=solid | label=dip | domain=logging | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class LoggingGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class LoggingHttpGateway(LoggingGateway):
    def send(self, payload: str) -> str:
        return f"http-logging:{payload}"

class LoggingAppService:
    def __init__(self, gateway: LoggingGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
