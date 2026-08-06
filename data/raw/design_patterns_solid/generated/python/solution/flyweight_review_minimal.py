"""DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=review | tier=minimal"""
from __future__ import annotations

class ReviewFlyweightFactory:
    def __init__(self) -> None:
        self._cache: dict[str, str] = {}

    def intern(self, key: str) -> str:
        if key not in self._cache:
            self._cache[key] = f"fw-review-{key}"
        return self._cache[key]

    def size(self) -> int:
        return len(self._cache)
