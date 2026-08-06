"""DesignPatternsSolid | kind=solid | label=dip | domain=notes | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class NotesGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class NotesHttpGateway(NotesGateway):
    def send(self, payload: str) -> str:
        return f"http-notes:{payload}"

class NotesAppService:
    def __init__(self, gateway: NotesGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
