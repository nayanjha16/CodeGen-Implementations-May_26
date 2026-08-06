"""DesignPatternsSolid | kind=design_pattern | label=state | domain=review | tier=logging"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class ReviewState(ABC):
    @abstractmethod
    def handle(self, ctx: "ReviewContext") -> str: ...

class ReviewOnState(ReviewState):
    def handle(self, ctx: "ReviewContext") -> str:
        ctx.set_state(ReviewOffState())
        return "was-on-review"

class ReviewOffState(ReviewState):
    def handle(self, ctx: "ReviewContext") -> str:
        ctx.set_state(ReviewOnState())
        return "was-off-review"

class ReviewContext:
    def __init__(self) -> None:
        self.state: ReviewState = ReviewOffState()

    def set_state(self, state: ReviewState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
