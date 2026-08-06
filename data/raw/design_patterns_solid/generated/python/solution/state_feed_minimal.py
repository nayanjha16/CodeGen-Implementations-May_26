"""DesignPatternsSolid | kind=design_pattern | label=state | domain=feed | tier=minimal"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class FeedState(ABC):
    @abstractmethod
    def handle(self, ctx: "FeedContext") -> str: ...

class FeedOnState(FeedState):
    def handle(self, ctx: "FeedContext") -> str:
        ctx.set_state(FeedOffState())
        return "was-on-feed"

class FeedOffState(FeedState):
    def handle(self, ctx: "FeedContext") -> str:
        ctx.set_state(FeedOnState())
        return "was-off-feed"

class FeedContext:
    def __init__(self) -> None:
        self.state: FeedState = FeedOffState()

    def set_state(self, state: FeedState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
