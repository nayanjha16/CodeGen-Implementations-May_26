"""DesignPatternsSolid | kind=design_pattern | label=mediator | domain=todo | tier=errors"""
from __future__ import annotations

class TodoMediator:
    def __init__(self) -> None:
        self.log: list[str] = []

    def notify(self, fr: str, msg: str) -> None:
        self.log.append(f"{fr}->{msg}")

    def history(self) -> str:
        return "|".join(self.log)

    def domain(self) -> str:
        return "todo"

class TodoColleague:
    def __init__(self, name: str, mediator: TodoMediator) -> None:
        self.name = name
        self.mediator = mediator

    def send(self, msg: str) -> None:
        self.mediator.notify(self.name, msg)
