"""DesignPatternsSolid | kind=solid | label=dip | domain=backup | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BackupGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class BackupHttpGateway(BackupGateway):
    def send(self, payload: str) -> str:
        return f"http-backup:{payload}"

class BackupAppService:
    def __init__(self, gateway: BackupGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
