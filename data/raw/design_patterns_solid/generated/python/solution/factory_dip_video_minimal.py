"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=video | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class VideoProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class VideoBasicProduct(VideoProduct):
    def operate(self) -> str:
        return "basic-video"

class VideoPremiumProduct(VideoProduct):
    def operate(self) -> str:
        return "premium-video"

class VideoFactory:
    def create(self, type_name: str) -> VideoProduct:
        if type_name.lower() == "premium":
            return VideoPremiumProduct()
        return VideoBasicProduct()
