"""DesignPatternsSolid | kind=design_pattern | label=iterator | domain=email | tier=minimal"""
from __future__ import annotations

from typing import Iterator

class EmailCollection:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, v: str) -> None:
        self.items.append(v)

    def __iter__(self) -> Iterator[str]:
        return iter(self.items)

    def join(self) -> str:
        return "email" + "".join(f":{it}" for it in self)
