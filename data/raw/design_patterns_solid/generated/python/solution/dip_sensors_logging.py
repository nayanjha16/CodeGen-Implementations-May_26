"""DesignPatternsSolid | kind=solid | label=dip | domain=sensors | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SensorsGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class SensorsHttpGateway(SensorsGateway):
    def send(self, payload: str) -> str:
        return f"http-sensors:{payload}"

class SensorsAppService:
    def __init__(self, gateway: SensorsGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
