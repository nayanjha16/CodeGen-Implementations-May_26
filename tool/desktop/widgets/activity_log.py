"""Scrollable structured activity log widget."""

from __future__ import annotations

import json
import tkinter as tk
from datetime import datetime
from tkinter import ttk

import customtkinter as ctk

from tool.core.activity_logger import ActivityEvent

# Events omitted from summary view (internal / noisy).
_SUMMARY_SKIP = frozenset(
    {
        "render_start",
        "render_complete",
        "schema_load_start",
        "schema_selection_start",
        "embedding_model_loaded",
        "fastapi_request_start",
        "inference_mode_selected",
    }
)


class ActivityLogPanel(ctk.CTkFrame):
    _ICONS = {"debug": "·", "info": "●", "warning": "⚠", "error": "✕"}
    _PLACEHOLDER = "Events appear here when you Execute or run connection tests.\n"

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._show_details = False
        self._events: list[ActivityEvent] = []

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=8, pady=(8, 4))
        ctk.CTkLabel(header, text="Activity Log", font=ctk.CTkFont(size=14, weight="bold")).pack(
            side="left", anchor="w"
        )
        self._detail_switch = ctk.CTkSwitch(
            header,
            text="Details",
            width=40,
            command=self._on_toggle_details,
        )
        self._detail_switch.pack(side="right")

        text_frame = ctk.CTkFrame(self)
        text_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self._text = tk.Text(
            text_frame,
            wrap="word",
            width=1,
            state="disabled",
            font=("Menlo", 11),
            bg="#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "#f5f5f5",
            fg="#dcdcdc" if ctk.get_appearance_mode() == "Dark" else "#1a1a1a",
            borderwidth=0,
            highlightthickness=0,
        )
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self._text.yview)
        self._text.configure(yscrollcommand=scrollbar.set)
        self._text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self._showing_placeholder = True
        self._append_placeholder()

    def _on_toggle_details(self) -> None:
        self._show_details = bool(self._detail_switch.get())
        self.render(self._events)

    @staticmethod
    def _short_time(iso_ts: str) -> str:
        try:
            dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
            return dt.strftime("%H:%M:%S")
        except ValueError:
            return iso_ts[:8] if len(iso_ts) >= 8 else iso_ts

    @classmethod
    def _summary_line(cls, event: ActivityEvent) -> str | None:
        if event.event in _SUMMARY_SKIP:
            return None
        if event.level == "debug":
            return None

        icon = cls._ICONS.get(event.level, "•")
        ts = cls._short_time(event.timestamp)
        details = event.details

        if event.event == "connection_established":
            db = details.get("database", "")
            return f"{icon} {ts}  Connected · {details.get('connection', db)}"
        if event.event == "connection_failed":
            return f"{icon} {ts}  Connection failed · {details.get('error', event.message)}"
        if event.event == "schema_loaded":
            return f"{icon} {ts}  Schema loaded · {details.get('table_count', '?')} tables"
        if event.event == "tables_selected":
            names = details.get("selected") or details.get("tables") or []
            preview = ", ".join(names[:4])
            if len(names) > 4:
                preview += f", +{len(names) - 4} more"
            method = details.get("method", "")
            if method == "sql_parse":
                return f"{icon} {ts}  Tables selected from SQL · {preview or event.message}"
            return f"{icon} {ts}  Tables selected · {preview or event.message}"
        if event.event == "sql_tables_parsed":
            parsed = details.get("parsed") or []
            preview = ", ".join(parsed[:4])
            if len(parsed) > 4:
                preview += f", +{len(parsed) - 4} more"
            return f"{icon} {ts}  Tables parsed from SQL · {preview or 'none'}"
        if event.event == "sql_tables_unknown":
            unknown = details.get("unknown") or []
            return f"{icon} {ts}  Unknown SQL tables · {', '.join(unknown)}"
        if event.event == "fk_tables_expanded":
            added = details.get("added") or []
            return f"{icon} {ts}  FK tables added · {', '.join(added)}"
        if event.event == "prompt_built":
            tables = details.get("tables") or []
            return f"{icon} {ts}  Prompt built · {len(tables)} tables, {details.get('prompt_length', '?')} chars"
        if event.event == "prompt_body":
            length = len(details.get("prompt") or "")
            return f"{icon} {ts}  Prompt payload · {length} chars (enable Details for full text)"
        if event.event == "doc_prompt_built":
            return f"{icon} {ts}  Doc prompt built · {details.get('prompt_length', '?')} chars"
        if event.event == "doc_prompt_body":
            length = len(details.get("prompt") or "")
            return f"{icon} {ts}  Doc prompt payload · {length} chars (enable Details for full text)"
        if event.event == "nosql_generated":
            length = details.get("nosql_length") or len(details.get("nosql") or "")
            return f"{icon} {ts}  NoSQL generated · {length} chars"
        if event.event == "documentation_start":
            return f"{icon} {ts}  Generating documentation · {details.get('prompt_length', '?')} chars"
        if event.event == "documentation_generated":
            length = details.get("doc_length") or len(details.get("documentation") or "")
            return f"{icon} {ts}  Documentation generated · {length} chars"
        if event.event == "documentation_ready":
            length = len(details.get("documentation") or "")
            return f"{icon} {ts}  Documentation ready · {length} chars"
        if event.event == "sql_generated":
            length = details.get("sql_length") or len(details.get("sql") or "")
            return f"{icon} {ts}  SQL generated · {length} chars"
        if event.event == "sql_generation_failed":
            return f"{icon} {ts}  SQL generation failed · {event.message}"
        if event.event in ("validation_start",):
            return f"{icon} {ts}  Validating SQL"
        if event.event == "validation_passed":
            return f"{icon} {ts}  Validation passed"
        if event.event == "validation_failed":
            return f"{icon} {ts}  Validation failed · {event.message}"
        if event.event == "executing":
            return f"{icon} {ts}  Executing query"
        if event.event == "rows_retrieved":
            rows = details.get("row_count", "?")
            ms = details.get("duration_ms", "?")
            truncated = " (truncated)" if details.get("truncated") else ""
            return f"{icon} {ts}  Results · {rows} rows in {ms} ms{truncated}"
        if event.event == "pipeline_failed":
            return f"{icon} {ts}  Pipeline failed · {details.get('error', event.message)}"

        return f"{icon} {ts}  [{event.stage}] {event.message}"

    @classmethod
    def _format_details(cls, event: ActivityEvent) -> str:
        if not event.details:
            return ""

        details = dict(event.details)
        prompt = details.pop("prompt", None)

        parts: list[str] = []
        if details:
            parts.append(
                "    " + json.dumps(details, indent=2, default=str).replace("\n", "\n    ") + "\n"
            )

        if isinstance(prompt, str) and prompt:
            parts.append(f"    --- prompt ({len(prompt)} chars) ---\n")
            for line in prompt.splitlines():
                parts.append(f"    {line}\n")
            parts.append("    --- end prompt ---\n")

        return "".join(parts)

    @classmethod
    def _format_event(cls, event: ActivityEvent, *, show_details: bool) -> str:
        if not show_details:
            summary = cls._summary_line(event)
            if summary is None:
                return ""
            return summary + "\n"

        icon = cls._ICONS.get(event.level, "•")
        ts = cls._short_time(event.timestamp)
        lines = [f"{icon} {ts}  [{event.stage}] {event.event}\n", f"    {event.message}\n"]
        if event.details:
            lines.append(cls._format_details(event))
        lines.append("\n")
        return "".join(lines)

    def _append_placeholder(self) -> None:
        self._text.configure(state="normal")
        self._text.insert("end", self._PLACEHOLDER)
        self._text.configure(state="disabled")

    def clear(self) -> None:
        self._events.clear()
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._showing_placeholder = True
        self._append_placeholder()

    def append_event(self, event: ActivityEvent) -> None:
        self._events.append(event)
        formatted = self._format_event(event, show_details=self._show_details)
        if not formatted:
            return

        self._text.configure(state="normal")
        if self._showing_placeholder:
            self._text.delete("1.0", "end")
            self._showing_placeholder = False
        self._text.insert("end", formatted)
        self._text.configure(state="disabled")
        self._text.see("end")

    def render(self, events: list[ActivityEvent]) -> None:
        self._events = list(events)
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        if not events:
            self._showing_placeholder = True
            self._append_placeholder()
        else:
            self._showing_placeholder = False
            for event in events[-120:]:
                line = self._format_event(event, show_details=self._show_details)
                if line:
                    self._text.insert("end", line)
        self._text.configure(state="disabled")
        self._text.see("end")
