"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=review | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ReviewService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class ReviewRealService(ReviewService):
    def load(self, id: str) -> str:
        return f"real-review:{id}"

class ReviewProxy(ReviewService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: ReviewRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = ReviewRealService()
        return self._real.load(id)
