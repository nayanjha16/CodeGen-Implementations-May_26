"""DesignPatternsSolid | kind=design_pattern | label=state | domain=booking | tier=minimal"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class BookingState(ABC):
    @abstractmethod
    def handle(self, ctx: "BookingContext") -> str: ...

class BookingOnState(BookingState):
    def handle(self, ctx: "BookingContext") -> str:
        ctx.set_state(BookingOffState())
        return "was-on-booking"

class BookingOffState(BookingState):
    def handle(self, ctx: "BookingContext") -> str:
        ctx.set_state(BookingOnState())
        return "was-off-booking"

class BookingContext:
    def __init__(self) -> None:
        self.state: BookingState = BookingOffState()

    def set_state(self, state: BookingState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
