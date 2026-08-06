"""DesignPatternsSolid | kind=design_pattern | label=memento | domain=sms | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class SmsMemento:
    state: str

class SmsOriginator:
    def __init__(self) -> None:
        self.state = "sms-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> SmsMemento:
        return SmsMemento(self.state)

    def restore(self, m: SmsMemento) -> None:
        self.state = m.state
