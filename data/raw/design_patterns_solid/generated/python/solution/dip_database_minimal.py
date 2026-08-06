"""DesignPatternsSolid | kind=solid | label=dip | domain=database | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DatabaseGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class DatabaseHttpGateway(DatabaseGateway):
    def send(self, payload: str) -> str:
        return f"http-database:{payload}"

class DatabaseAppService:
    def __init__(self, gateway: DatabaseGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
