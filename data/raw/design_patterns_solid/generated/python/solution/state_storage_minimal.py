"""DesignPatternsSolid | kind=design_pattern | label=state | domain=storage | tier=minimal"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class StorageState(ABC):
    @abstractmethod
    def handle(self, ctx: "StorageContext") -> str: ...

class StorageOnState(StorageState):
    def handle(self, ctx: "StorageContext") -> str:
        ctx.set_state(StorageOffState())
        return "was-on-storage"

class StorageOffState(StorageState):
    def handle(self, ctx: "StorageContext") -> str:
        ctx.set_state(StorageOnState())
        return "was-off-storage"

class StorageContext:
    def __init__(self) -> None:
        self.state: StorageState = StorageOffState()

    def set_state(self, state: StorageState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
