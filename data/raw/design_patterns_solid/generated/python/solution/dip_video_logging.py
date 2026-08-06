"""DesignPatternsSolid | kind=solid | label=dip | domain=video | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class VideoGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class VideoHttpGateway(VideoGateway):
    def send(self, payload: str) -> str:
        return f"http-video:{payload}"

class VideoAppService:
    def __init__(self, gateway: VideoGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
