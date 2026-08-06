"""DesignPatternsSolid | kind=solid | label=dip | domain=analytics | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AnalyticsGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class AnalyticsHttpGateway(AnalyticsGateway):
    def send(self, payload: str) -> str:
        return f"http-analytics:{payload}"

class AnalyticsAppService:
    def __init__(self, gateway: AnalyticsGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
