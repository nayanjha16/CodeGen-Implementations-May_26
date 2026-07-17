"""Table selection panel — user confirms schema before SQL generation."""

from __future__ import annotations

import customtkinter as ctk

from tool.core.schema_loader import TableSchema

_SCROLL_HEIGHT = 88  # ~4 checkbox rows at height 20


class TableSelectorPanel(ctk.CTkFrame):
    """Checklist of suggested tables; optional expand to all schema tables."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._checkboxes: dict[str, ctk.CTkCheckBox] = {}
        self._vars: dict[str, ctk.StringVar] = {}
        self._scores: dict[str, float] = {}
        self._all_tables: list[TableSchema] = []
        self._suggested: list[str] = []
        self._show_all = False
        self._locked = False

        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=4, pady=(0, 0))
        ctk.CTkLabel(header, text="Schema Tables", font=ctk.CTkFont(size=13, weight="bold")).pack(
            side="left", anchor="w"
        )
        self._show_all_btn = ctk.CTkButton(
            header,
            text="Show all",
            width=72,
            height=22,
            command=self._toggle_show_all,
        )
        self._show_all_btn.pack(side="right")

        self._hint = ctk.CTkLabel(
            self,
            text="Review suggested tables, then Run Query",
            text_color="gray",
            font=ctk.CTkFont(size=11),
            anchor="w",
        )
        self._hint.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 2))

        # Fixed-height shell — CTkScrollableFrame otherwise grows with checkbox content.
        self._scroll_shell = ctk.CTkFrame(self, height=_SCROLL_HEIGHT, corner_radius=6)
        self._scroll_shell.grid(row=2, column=0, sticky="ew", padx=4, pady=(0, 2))
        self._scroll_shell.grid_propagate(False)
        self._scroll_shell.grid_columnconfigure(0, weight=1)
        self._scroll_shell.grid_rowconfigure(0, weight=1)

        self._scroll = ctk.CTkScrollableFrame(self._scroll_shell, height=_SCROLL_HEIGHT - 4)
        self._scroll.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

        self._placeholder = ctk.CTkLabel(
            self._scroll,
            text="Suggested tables appear after Execute.",
            text_color="gray",
            anchor="w",
            font=ctk.CTkFont(size=11),
        )
        self._placeholder.pack(fill="x", padx=2, pady=2)

    @property
    def is_locked(self) -> bool:
        return self._locked

    def clear(self) -> None:
        self._locked = False
        self._show_all = False
        self._scores.clear()
        self._all_tables.clear()
        self._suggested.clear()
        self._vars.clear()
        for widget in self._scroll.winfo_children():
            widget.destroy()
        self._checkboxes.clear()
        self._show_all_btn.configure(text="Show all")
        self._placeholder = ctk.CTkLabel(
            self._scroll,
            text="Suggested tables appear after Execute.",
            text_color="gray",
            anchor="w",
            font=ctk.CTkFont(size=11),
        )
        self._placeholder.pack(fill="x", padx=2, pady=2)
        self._hint.configure(text="Review suggested tables, then Run Query")

    def set_tables(
        self,
        tables: list[TableSchema],
        suggested: list[str],
        scores: dict[str, float] | None = None,
    ) -> None:
        self._locked = False
        self._show_all = False
        self._all_tables = list(tables)
        self._suggested = list(suggested)
        self._scores = dict(scores or {})
        self._show_all_btn.configure(text="Show all")
        self._render_checkboxes()
        self._hint.configure(text=f"{len(suggested)} suggested — adjust if needed, then Run Query")

    def _toggle_show_all(self) -> None:
        if self._locked or not self._all_tables:
            return
        self._show_all = not self._show_all
        self._show_all_btn.configure(text="Suggested" if self._show_all else "Show all")
        self._render_checkboxes()

    def _render_checkboxes(self) -> None:
        current = set(self.get_selected()) if self._checkboxes else set(self._suggested)
        if not current:
            current = set(self._suggested)

        for widget in self._scroll.winfo_children():
            widget.destroy()
        self._checkboxes.clear()
        self._vars.clear()

        if not self._all_tables:
            ctk.CTkLabel(self._scroll, text="No tables found.", text_color="gray", font=ctk.CTkFont(size=11)).pack(
                anchor="w", padx=2, pady=2
            )
            return

        visible = self._all_tables if self._show_all else [t for t in self._all_tables if t.name in self._suggested]
        if not visible:
            visible = [t for t in self._all_tables if t.name in self._suggested]

        for table in sorted(visible, key=lambda t: t.name):
            score = self._scores.get(table.name)
            suffix = f" ({score:.2f})" if score is not None and score > 0 else ""
            var = ctk.StringVar(value="off")
            cb = ctk.CTkCheckBox(
                self._scroll,
                text=f"{table.name}{suffix}",
                variable=var,
                onvalue="on",
                offvalue="off",
                height=20,
                checkbox_height=16,
                checkbox_width=16,
                font=ctk.CTkFont(size=11),
            )
            cb.pack(anchor="w", padx=2, pady=0)
            if table.name in current:
                cb.select()
            self._checkboxes[table.name] = cb
            self._vars[table.name] = var

        self._scroll.configure(height=_SCROLL_HEIGHT - 4)

    def get_selected(self) -> list[str]:
        selected: list[str] = []
        for name, var in self._vars.items():
            if var.get() == "on":
                selected.append(name)
        ordered = [name for name in self._suggested if name in selected]
        extras = [name for name in selected if name not in self._suggested]
        return ordered + sorted(extras)

    def lock(self) -> None:
        self._locked = True
        self._show_all_btn.configure(state="disabled")
        for cb in self._checkboxes.values():
            cb.configure(state="disabled")
        self._hint.configure(text="Table selection locked")

    def unlock(self) -> None:
        self._locked = False
        self._show_all_btn.configure(state="normal")
        for cb in self._checkboxes.values():
            cb.configure(state="normal")
