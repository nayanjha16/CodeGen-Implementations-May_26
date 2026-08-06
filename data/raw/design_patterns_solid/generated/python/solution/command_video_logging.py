"""DesignPatternsSolid | kind=design_pattern | label=command | domain=video | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class VideoCommand(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class VideoReceiver:
    def action(self, x: str) -> str:
        return f"done-video:{x}"

class VideoActionCommand(VideoCommand):
    def __init__(self, receiver: VideoReceiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
