"""DesignPatternsSolid | kind=design_pattern | label=state | domain=canvas | tier=minimal"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class CanvasState(ABC):
    @abstractmethod
    def handle(self, ctx: "CanvasContext") -> str: ...

class CanvasOnState(CanvasState):
    def handle(self, ctx: "CanvasContext") -> str:
        ctx.set_state(CanvasOffState())
        return "was-on-canvas"

class CanvasOffState(CanvasState):
    def handle(self, ctx: "CanvasContext") -> str:
        ctx.set_state(CanvasOnState())
        return "was-off-canvas"

class CanvasContext:
    def __init__(self) -> None:
        self.state: CanvasState = CanvasOffState()

    def set_state(self, state: CanvasState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
