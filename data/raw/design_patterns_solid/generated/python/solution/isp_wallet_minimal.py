"""DesignPatternsSolid | kind=solid | label=isp | domain=wallet | tier=minimal"""
from __future__ import annotations

from typing import Protocol

class WalletReadable(Protocol):
    def read(self) -> str: ...

class WalletWritable(Protocol):
    def write(self, v: str) -> None: ...

class WalletStore:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"wallet:{v}"

def mirror(r: WalletReadable) -> str:
    return r.read()
