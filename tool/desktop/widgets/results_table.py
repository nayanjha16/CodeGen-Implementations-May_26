"""Pandas DataFrame table widget using ttk.Treeview."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import customtkinter as ctk
import pandas as pd


class ResultsTable(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        ctk.CTkLabel(self, text="Execution Output", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=8, pady=(8, 4)
        )

        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=8, pady=(0, 4))

        self._tree = ttk.Treeview(table_frame, show="headings", selectmode="browse")
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self._tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self._tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self._meta = ctk.CTkLabel(self, text="", anchor="w", justify="left")
        self._meta.pack(fill="x", padx=8, pady=(0, 8))

    def render(
        self,
        df: pd.DataFrame | None,
        meta: dict | None = None,
        selected_tables: list[str] | None = None,
    ) -> None:
        self._tree.delete(*self._tree.get_children())
        parts: list[str] = []

        if df is None:
            parts.append("Results will appear here after a successful Execute.")
        elif df.empty:
            parts.append("Query returned no rows.")
        else:
            cols = [str(c) for c in df.columns]
            self._tree["columns"] = cols
            for col in cols:
                self._tree.heading(col, text=col)
                self._tree.column(col, width=max(80, min(200, len(col) * 10)), stretch=True)
            for row in df.itertuples(index=False, name=None):
                values = ["" if v is None else str(v) for v in row]
                self._tree.insert("", "end", values=values)

        meta = meta or {}
        if "row_count" in meta:
            parts.append(f"Rows: {meta['row_count']}")
        if "duration_ms" in meta:
            parts.append(f"Duration: {meta['duration_ms']} ms")
        if meta.get("truncated"):
            parts.append("Truncated: yes")
        if selected_tables:
            parts.append(f"Tables: {', '.join(selected_tables)}")

        self._meta.configure(text="  ·  ".join(parts) if parts else "")
