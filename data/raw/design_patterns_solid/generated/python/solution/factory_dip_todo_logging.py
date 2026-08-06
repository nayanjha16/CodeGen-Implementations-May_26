"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=todo | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TodoProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class TodoBasicProduct(TodoProduct):
    def operate(self) -> str:
        return "basic-todo"

class TodoPremiumProduct(TodoProduct):
    def operate(self) -> str:
        return "premium-todo"

class TodoFactory:
    def create(self, type_name: str) -> TodoProduct:
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return TodoPremiumProduct()
        return TodoBasicProduct()
