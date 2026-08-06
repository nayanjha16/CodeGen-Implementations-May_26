"""DesignPatternsSolid | kind=solid | label=dip | domain=auth | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AuthGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class AuthHttpGateway(AuthGateway):
    def send(self, payload: str) -> str:
        return f"http-auth:{payload}"

class AuthAppService:
    def __init__(self, gateway: AuthGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
