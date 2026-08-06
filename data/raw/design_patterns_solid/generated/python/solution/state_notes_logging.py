"""DesignPatternsSolid | kind=design_pattern | label=state | domain=notes | tier=logging"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class NotesState(ABC):
    @abstractmethod
    def handle(self, ctx: "NotesContext") -> str: ...

class NotesOnState(NotesState):
    def handle(self, ctx: "NotesContext") -> str:
        ctx.set_state(NotesOffState())
        return "was-on-notes"

class NotesOffState(NotesState):
    def handle(self, ctx: "NotesContext") -> str:
        ctx.set_state(NotesOnState())
        return "was-off-notes"

class NotesContext:
    def __init__(self) -> None:
        self.state: NotesState = NotesOffState()

    def set_state(self, state: NotesState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
