"""DesignPatternsSolid | kind=design_pattern | label=composite | domain=wallet | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WalletNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class WalletLeaf(WalletNode):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class WalletComposite(WalletNode):
    def __init__(self) -> None:
        self.children: list[WalletNode] = []

    def add(self, n: WalletNode) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
