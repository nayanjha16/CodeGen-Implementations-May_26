"""DesignPatternsSolid | kind=design_pattern | label=flyweight | domain=map | tier=errors"""
from __future__ import annotations

class MapFlyweightFactory:
    def __init__(self) -> None:
        self._cache: dict[str, str] = {}

    def intern(self, key: str) -> str:
        if key not in self._cache:
            self._cache[key] = f"fw-map-{key}"
        return self._cache[key]

    def size(self) -> int:
        return len(self._cache)
