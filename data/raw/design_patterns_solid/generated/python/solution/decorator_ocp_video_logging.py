"""DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=video | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class VideoComponent(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class VideoCore(VideoComponent):
    def process(self, input: str) -> str:
        return f"video:{input}"

class VideoUpperDecorator(VideoComponent):
    def __init__(self, inner: VideoComponent) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
