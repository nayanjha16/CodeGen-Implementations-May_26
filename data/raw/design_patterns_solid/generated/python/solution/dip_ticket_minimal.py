"""DesignPatternsSolid | kind=solid | label=dip | domain=ticket | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TicketGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class TicketHttpGateway(TicketGateway):
    def send(self, payload: str) -> str:
        return f"http-ticket:{payload}"

class TicketAppService:
    def __init__(self, gateway: TicketGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
