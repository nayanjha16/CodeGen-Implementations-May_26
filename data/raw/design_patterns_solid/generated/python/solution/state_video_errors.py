"""DesignPatternsSolid | kind=design_pattern | label=state | domain=video | tier=errors"""
from __future__ import annotations

from __future__ import annotations
from abc import ABC, abstractmethod

class VideoState(ABC):
    @abstractmethod
    def handle(self, ctx: "VideoContext") -> str: ...

class VideoOnState(VideoState):
    def handle(self, ctx: "VideoContext") -> str:
        ctx.set_state(VideoOffState())
        return "was-on-video"

class VideoOffState(VideoState):
    def handle(self, ctx: "VideoContext") -> str:
        ctx.set_state(VideoOnState())
        return "was-off-video"

class VideoContext:
    def __init__(self) -> None:
        self.state: VideoState = VideoOffState()

    def set_state(self, state: VideoState) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
