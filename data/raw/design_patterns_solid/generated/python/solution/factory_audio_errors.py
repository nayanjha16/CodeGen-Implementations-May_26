"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=audio | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AudioProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class AudioBasicProduct(AudioProduct):
    def operate(self) -> str:
        return "basic-audio"

class AudioPremiumProduct(AudioProduct):
    def operate(self) -> str:
        return "premium-audio"

class AudioFactory:
    def create(self, type_name: str) -> AudioProduct:
        if not type_name:
            raise ValueError("type required")
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return AudioPremiumProduct()
        return AudioBasicProduct()
