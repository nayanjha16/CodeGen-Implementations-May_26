"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=game | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class GameImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class GameFileImpl(GameImpl):
    def write(self, msg: str) -> str:
        return f"file:game:{msg}"

class GameMemoryImpl(GameImpl):
    def write(self, msg: str) -> str:
        return f"mem:game:{msg}"

class GameBridge(ABC):
    def __init__(self, impl: GameImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class GameAlertBridge(GameBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
