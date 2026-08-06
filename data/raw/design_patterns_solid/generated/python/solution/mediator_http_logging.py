"""DesignPatternsSolid | kind=design_pattern | label=mediator | domain=http | tier=logging"""
from __future__ import annotations

class HttpMediator:
    def __init__(self) -> None:
        self.log: list[str] = []

    def notify(self, fr: str, msg: str) -> None:
        self.log.append(f"{fr}->{msg}")

    def history(self) -> str:
        return "|".join(self.log)

    def domain(self) -> str:
        return "http"

class HttpColleague:
    def __init__(self, name: str, mediator: HttpMediator) -> None:
        self.name = name
        self.mediator = mediator

    def send(self, msg: str) -> None:
        self.mediator.notify(self.name, msg)
