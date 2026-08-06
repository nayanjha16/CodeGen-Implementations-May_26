"""DesignPatternsSolid | kind=design_pattern | label=state | domain=map | tier=errors"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class MapState(ABC):
    @abstractmethod
    def handle(self, ctx: "MapContext") -> str: ...

class MapOnState(MapState):
    def handle(self, ctx: "MapContext") -> str:
        ctx.set_state(MapOffState())
        return "was-on-map"

class MapOffState(MapState):
    def handle(self, ctx: "MapContext") -> str:
        ctx.set_state(MapOnState())
        return "was-off-map"

class MapContext:
    def __init__(self) -> None:
        self.state: MapState = MapOffState()

    def set_state(self, state: MapState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
