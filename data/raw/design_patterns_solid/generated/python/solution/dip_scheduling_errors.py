"""DesignPatternsSolid | kind=solid | label=dip | domain=scheduling | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SchedulingGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class SchedulingHttpGateway(SchedulingGateway):
    def send(self, payload: str) -> str:
        return f"http-scheduling:{payload}"

class SchedulingAppService:
    def __init__(self, gateway: SchedulingGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
