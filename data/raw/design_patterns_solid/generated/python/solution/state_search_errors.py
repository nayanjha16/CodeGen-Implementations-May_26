"""DesignPatternsSolid | kind=design_pattern | label=state | domain=search | tier=errors"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class SearchState(ABC):
    @abstractmethod
    def handle(self, ctx: "SearchContext") -> str: ...

class SearchOnState(SearchState):
    def handle(self, ctx: "SearchContext") -> str:
        ctx.set_state(SearchOffState())
        return "was-on-search"

class SearchOffState(SearchState):
    def handle(self, ctx: "SearchContext") -> str:
        ctx.set_state(SearchOnState())
        return "was-off-search"

class SearchContext:
    def __init__(self) -> None:
        self.state: SearchState = SearchOffState()

    def set_state(self, state: SearchState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
