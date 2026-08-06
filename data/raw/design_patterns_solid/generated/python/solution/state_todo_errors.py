"""DesignPatternsSolid | kind=design_pattern | label=state | domain=todo | tier=errors"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class TodoState(ABC):
    @abstractmethod
    def handle(self, ctx: "TodoContext") -> str: ...

class TodoOnState(TodoState):
    def handle(self, ctx: "TodoContext") -> str:
        ctx.set_state(TodoOffState())
        return "was-on-todo"

class TodoOffState(TodoState):
    def handle(self, ctx: "TodoContext") -> str:
        ctx.set_state(TodoOnState())
        return "was-off-todo"

class TodoContext:
    def __init__(self) -> None:
        self.state: TodoState = TodoOffState()

    def set_state(self, state: TodoState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
