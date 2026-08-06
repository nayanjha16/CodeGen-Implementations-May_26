"""DesignPatternsSolid | kind=solid | label=dip | domain=search | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SearchGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class SearchHttpGateway(SearchGateway):
    def send(self, payload: str) -> str:
        return f"http-search:{payload}"

class SearchAppService:
    def __init__(self, gateway: SearchGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
