"""DesignPatternsSolid | kind=design_pattern | label=state | domain=sync | tier=minimal"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class SyncState(ABC):
    @abstractmethod
    def handle(self, ctx: "SyncContext") -> str: ...

class SyncOnState(SyncState):
    def handle(self, ctx: "SyncContext") -> str:
        ctx.set_state(SyncOffState())
        return "was-on-sync"

class SyncOffState(SyncState):
    def handle(self, ctx: "SyncContext") -> str:
        ctx.set_state(SyncOnState())
        return "was-off-sync"

class SyncContext:
    def __init__(self) -> None:
        self.state: SyncState = SyncOffState()

    def set_state(self, state: SyncState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
