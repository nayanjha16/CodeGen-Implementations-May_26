"""DesignPatternsSolid | kind=solid | label=dip | domain=feed | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class FeedGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class FeedHttpGateway(FeedGateway):
    def send(self, payload: str) -> str:
        return f"http-feed:{payload}"

class FeedAppService:
    def __init__(self, gateway: FeedGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
