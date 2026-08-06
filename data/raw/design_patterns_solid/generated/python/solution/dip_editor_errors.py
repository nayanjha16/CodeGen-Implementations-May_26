"""DesignPatternsSolid | kind=solid | label=dip | domain=editor | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class EditorGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class EditorHttpGateway(EditorGateway):
    def send(self, payload: str) -> str:
        return f"http-editor:{payload}"

class EditorAppService:
    def __init__(self, gateway: EditorGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
