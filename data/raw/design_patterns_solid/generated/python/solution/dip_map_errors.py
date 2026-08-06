"""DesignPatternsSolid | kind=solid | label=dip | domain=map | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MapGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class MapHttpGateway(MapGateway):
    def send(self, payload: str) -> str:
        return f"http-map:{payload}"

class MapAppService:
    def __init__(self, gateway: MapGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
