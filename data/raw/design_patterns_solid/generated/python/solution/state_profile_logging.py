"""DesignPatternsSolid | kind=design_pattern | label=state | domain=profile | tier=logging"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class ProfileState(ABC):
    @abstractmethod
    def handle(self, ctx: "ProfileContext") -> str: ...

class ProfileOnState(ProfileState):
    def handle(self, ctx: "ProfileContext") -> str:
        ctx.set_state(ProfileOffState())
        return "was-on-profile"

class ProfileOffState(ProfileState):
    def handle(self, ctx: "ProfileContext") -> str:
        ctx.set_state(ProfileOnState())
        return "was-off-profile"

class ProfileContext:
    def __init__(self) -> None:
        self.state: ProfileState = ProfileOffState()

    def set_state(self, state: ProfileState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
