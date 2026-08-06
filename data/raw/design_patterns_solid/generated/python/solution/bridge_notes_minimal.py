"""DesignPatternsSolid | kind=design_pattern | label=bridge | domain=notes | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class NotesImpl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class NotesFileImpl(NotesImpl):
    def write(self, msg: str) -> str:
        return f"file:notes:{msg}"

class NotesMemoryImpl(NotesImpl):
    def write(self, msg: str) -> str:
        return f"mem:notes:{msg}"

class NotesBridge(ABC):
    def __init__(self, impl: NotesImpl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class NotesAlertBridge(NotesBridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
