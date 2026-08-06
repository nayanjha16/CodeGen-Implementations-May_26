"""DesignPatternsSolid | kind=design_pattern | label=chain of responsibility | domain=notifications | tier=errors"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class NotificationsHandler(ABC):
    def __init__(self) -> None:
        self.next: NotificationsHandler | None = None

    def link(self, n: NotificationsHandler) -> NotificationsHandler:
        self.next = n
        return n

    def handle(self, level: int, msg: str) -> str:
        if self.can_handle(level):
            return self.do_handle(msg)
        if self.next is not None:
            return self.next.handle(level, msg)
        return "unhandled-notifications"

    @abstractmethod
    def can_handle(self, level: int) -> bool: ...
    @abstractmethod
    def do_handle(self, msg: str) -> str: ...

class NotificationsLowHandler(NotificationsHandler):
    def can_handle(self, level: int) -> bool:
        return level <= 1
    def do_handle(self, msg: str) -> str:
        return f"low-notifications:{msg}"

class NotificationsHighHandler(NotificationsHandler):
    def can_handle(self, level: int) -> bool:
        return level > 1
    def do_handle(self, msg: str) -> str:
        return f"high-notifications:{msg}"
