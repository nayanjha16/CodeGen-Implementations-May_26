"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=notifications | tier=minimal"""
from __future__ import annotations

class NotificationsValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class NotificationsWriter:
    def write(self, v: str) -> str:
        return f"wrote-notifications:{v}"

class NotificationsFacade:
    def __init__(self) -> None:
        self.validator = NotificationsValidator()
        self.writer = NotificationsWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
