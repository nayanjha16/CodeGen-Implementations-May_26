"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=notifications | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class NotificationsMemento:
    state: str

class NotificationsOriginator:
    def __init__(self) -> None:
        self.state = "notifications-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> NotificationsMemento:
        return NotificationsMemento(self.state)

    def restore(self, m: NotificationsMemento) -> None:
        self.state = m.state
