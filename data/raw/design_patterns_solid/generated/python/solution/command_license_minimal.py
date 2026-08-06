"""DesignPatternsSolid | kind=design_pattern | label=command | domain=license | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class LicenseCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class LicenseReceiver:
    def action(self, x: str) -> str:
        return f"done-license:{x}"

class LicenseActionCommand(LicenseCommand):
    def __init__(self, receiver: LicenseReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
