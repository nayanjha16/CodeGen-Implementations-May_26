"""DesignPatternsSolid | kind=solid | label=dip | domain=session | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SessionGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class SessionHttpGateway(SessionGateway):
    def send(self, payload: str) -> str:
        return f"http-session:{payload}"

class SessionAppService:
    def __init__(self, gateway: SessionGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
