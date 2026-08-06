"""DesignPatternsSolid | kind=design_pattern | label=state | domain=inventory | tier=logging"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class InventoryState(ABC):
    @abstractmethod
    def handle(self, ctx: "InventoryContext") -> str: ...

class InventoryOnState(InventoryState):
    def handle(self, ctx: "InventoryContext") -> str:
        ctx.set_state(InventoryOffState())
        return "was-on-inventory"

class InventoryOffState(InventoryState):
    def handle(self, ctx: "InventoryContext") -> str:
        ctx.set_state(InventoryOnState())
        return "was-off-inventory"

class InventoryContext:
    def __init__(self) -> None:
        self.state: InventoryState = InventoryOffState()

    def set_state(self, state: InventoryState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
