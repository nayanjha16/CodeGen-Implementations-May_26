"""DesignPatternsSolid | kind=solid | label=dip | domain=calendar | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CalendarGateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class CalendarHttpGateway(CalendarGateway):
    def send(self, payload: str) -> str:
        return f"http-calendar:{payload}"

class CalendarAppService:
    def __init__(self, gateway: CalendarGateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
