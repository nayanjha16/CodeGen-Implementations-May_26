"""DesignPatternsSolid | kind=solid | label=dip | domain=notifications | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class NotificationsGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class NotificationsHttpGateway(NotificationsGateway):
    def send(self, payload: str) -> str:
        return f"http-notifications:{payload}"

class NotificationsAppService:
    def __init__(self, gateway: NotificationsGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
