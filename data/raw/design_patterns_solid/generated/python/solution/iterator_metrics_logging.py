"""DesignPatternsSolid | kind=design_pattern | label=iterator | domain=metrics | tier=logging"""
from __future__ import annotations

from typing import Iterator

class MetricsCollection:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, v: str) -> None:
        self.items.append(v)

    def __iter__(self) -> Iterator[str]:
        return iter(self.items)

    def join(self) -> str:
        return "metrics" + "".join(f":{it}" for it in self)
