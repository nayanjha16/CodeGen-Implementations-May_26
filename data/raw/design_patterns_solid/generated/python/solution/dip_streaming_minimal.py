"""DesignPatternsSolid | kind=solid | label=dip | domain=streaming | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class StreamingGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class StreamingHttpGateway(StreamingGateway):
    def send(self, payload: str) -> str:
        return f"http-streaming:{payload}"

class StreamingAppService:
    def __init__(self, gateway: StreamingGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
