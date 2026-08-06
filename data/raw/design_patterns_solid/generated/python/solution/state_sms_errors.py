"""DesignPatternsSolid | kind=design_pattern | label=state | domain=sms | tier=errors"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class SmsState(ABC):
    @abstractmethod
    def handle(self, ctx: "SmsContext") -> str: ...

class SmsOnState(SmsState):
    def handle(self, ctx: "SmsContext") -> str:
        ctx.set_state(SmsOffState())
        return "was-on-sms"

class SmsOffState(SmsState):
    def handle(self, ctx: "SmsContext") -> str:
        ctx.set_state(SmsOnState())
        return "was-off-sms"

class SmsContext:
    def __init__(self) -> None:
        self.state: SmsState = SmsOffState()

    def set_state(self, state: SmsState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
