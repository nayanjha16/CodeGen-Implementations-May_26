"""Structured activity logging for the Streamlit UI."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

LogLevel = Literal["debug", "info", "warning", "error"]


@dataclass
class ActivityEvent:
    timestamp: str
    level: LogLevel
    stage: str
    event: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid4().hex[:12])

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


EventListener = Callable[["ActivityEvent"], None]


class ActivityLogger:
    """Append-only structured event buffer."""

    def __init__(
        self,
        events: list[ActivityEvent] | None = None,
        on_event: EventListener | None = None,
    ):
        self._events: list[ActivityEvent] = list(events or [])
        self._on_event = on_event

    def set_listener(self, on_event: EventListener | None) -> None:
        """Register or clear a callback invoked after each new event."""
        self._on_event = on_event

    @property
    def events(self) -> list[ActivityEvent]:
        return list(self._events)

    def clear(self) -> None:
        self._events.clear()

    def _emit(
        self,
        level: LogLevel,
        *,
        stage: str,
        event: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> ActivityEvent:
        entry = ActivityEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=level,
            stage=stage,
            event=event,
            message=message,
            details=details or {},
        )
        self._events.append(entry)
        if self._on_event is not None:
            self._on_event(entry)
        return entry

    def debug(self, *, stage: str, event: str, message: str, details: dict[str, Any] | None = None) -> ActivityEvent:
        return self._emit("debug", stage=stage, event=event, message=message, details=details)

    def info(self, *, stage: str, event: str, message: str, details: dict[str, Any] | None = None) -> ActivityEvent:
        return self._emit("info", stage=stage, event=event, message=message, details=details)

    def warning(self, *, stage: str, event: str, message: str, details: dict[str, Any] | None = None) -> ActivityEvent:
        return self._emit("warning", stage=stage, event=event, message=message, details=details)

    def error(self, *, stage: str, event: str, message: str, details: dict[str, Any] | None = None) -> ActivityEvent:
        return self._emit("error", stage=stage, event=event, message=message, details=details)
