"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=streaming | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class StreamingProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class StreamingBasicProduct(StreamingProduct):
    def operate(self) -> str:
        return "basic-streaming"

class StreamingPremiumProduct(StreamingProduct):
    def operate(self) -> str:
        return "premium-streaming"

class StreamingFactory:
    def create(self, type_name: str) -> StreamingProduct:
        if not type_name:
            raise ValueError("type required")
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return StreamingPremiumProduct()
        return StreamingBasicProduct()
