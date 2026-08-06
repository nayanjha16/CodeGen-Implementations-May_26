"""DesignPatternsSolid | kind=solid | label=dip | domain=sync | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SyncGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class SyncHttpGateway(SyncGateway):
    def send(self, payload: str) -> str:
        return f"http-sync:{payload}"

class SyncAppService:
    def __init__(self, gateway: SyncGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
