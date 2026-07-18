"""Main desktop application window."""

from __future__ import annotations

import threading
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image, ImageTk

from tool.config import ToolConfig
from tool.core.activity_logger import ActivityEvent
from tool.desktop.app_state import AppState
from tool.desktop.registry import build_adapters
from tool.desktop.macos import set_dock_icon, set_tk_app_name
from tool.desktop.settings_window import SettingsWindow
from tool.desktop.widgets.activity_log import ActivityLogPanel
from tool.desktop.widgets.results_table import ResultsTable
from tool.desktop.widgets.table_selector import TableSelectorPanel
from tool.pipeline.text2sql_pipeline import PrepareResult
from tool.pipeline.text2sql_pipeline import Text2SqlPipeline


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._cfg = ToolConfig.load()
        self.title(self._cfg.app.title)
        self.geometry("1200x820")
        self.minsize(900, 640)
        self._logo_photo = None
        self._header_logo = None
        self._apply_app_logo(self._cfg)
        set_tk_app_name(self, self._cfg.app.title)
        set_dock_icon(self._cfg.logo_file())

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.app_state = AppState()
        self.app_state.load_settings()
        self._pipeline = Text2SqlPipeline(settings=self.app_state.settings)
        self._adapters = build_adapters(pipeline=self._pipeline)
        self.adapter = self._adapters["Text-to-SQL"]

        self._prepare_result: PrepareResult | None = None
        self._awaiting_table_confirm = False
        self._run_locked = False
        self._last_query = ""

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_workspace()
        self._build_activity_panel()

        self.bind("<Control-Return>", lambda _e: self._on_execute())
        self.bind("<Command-Return>", lambda _e: self._on_execute())

    def _apply_app_logo(self, cfg: ToolConfig) -> None:
        logo_path = cfg.logo_file()
        if not logo_path.exists():
            return

        logo_image = Image.open(logo_path)
        self._logo_photo = ImageTk.PhotoImage(logo_image)
        self.iconphoto(True, self._logo_photo)
        self._header_logo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(36, 40))

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 4))

        title_col = 0
        if self._header_logo is not None:
            ctk.CTkLabel(header, text="", image=self._header_logo).grid(row=0, column=0, sticky="w", padx=(0, 10))
            title_col = 1

        header.grid_columnconfigure(title_col, weight=1)

        ctk.CTkLabel(
            header,
            text=self._cfg.app.title,
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=title_col, sticky="w")

        self._conn_label = ctk.CTkLabel(header, text="", font=ctk.CTkFont(size=12))
        self._conn_label.grid(row=0, column=title_col + 1, sticky="e", padx=(8, 12))
        ctk.CTkButton(header, text="Settings", width=90, command=self._open_settings).grid(
            row=0, column=title_col + 2, sticky="e"
        )

        self._refresh_connection_label()

        self._status_label = ctk.CTkLabel(self, text="", anchor="w", text_color="gray")
        self._status_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 4))

        self._tabs = ctk.CTkTabview(self)
        self._tabs.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=12, pady=4)
        self._tabs.add("Text-to-SQL")
        self._tabs.add("SQL-to-NoSQL")
        self._tabs.add("Documentation")

        self._build_text2sql_tab(self._tabs.tab("Text-to-SQL"))
        self._build_stub_tab(self._tabs.tab("SQL-to-NoSQL"), "SQL-to-NoSQL", "Coming soon — convert SQL to NoSQL using the same adapter pattern.")
        self._build_docs_tab(self._tabs.tab("Documentation"))

    def _build_workspace(self) -> None:
        pass  # workspace lives inside tabview

    def _build_activity_panel(self) -> None:
        pass  # activity log is embedded in Text-to-SQL tab layout

    def _refresh_connection_label(self) -> None:
        conn = self.app_state.settings.get_active_connection() if self.app_state.settings else None
        if conn:
            self._conn_label.configure(text=f"PostgreSQL · {conn.name} ({conn.host}:{conn.port}/{conn.database})")
        else:
            self._conn_label.configure(text="No database — open Settings")

    def _build_text2sql_tab(self, parent) -> None:
        parent.grid_columnconfigure(0, weight=3)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(parent, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(4, 8), pady=4)
        left.grid_rowconfigure(7, weight=1)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left, text="Natural Language Query", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(4, 4)
        )
        self._query_box = ctk.CTkTextbox(left, height=72)
        self._query_box.grid(row=1, column=0, sticky="ew", pady=(0, 4))
        self._query_box.insert("1.0", "count number of films")
        self._query_box.bind("<KeyRelease>", lambda _e: self._on_query_changed())

        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="w", pady=4)
        self._execute_btn = ctk.CTkButton(btn_row, text="Execute", command=self._on_execute, width=110)
        self._execute_btn.pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_row, text="Clear", command=self._on_clear, width=80).pack(side="left")
        ctk.CTkLabel(btn_row, text="  Ctrl/Cmd+Enter", text_color="gray").pack(side="left", padx=8)

        self._table_selector = TableSelectorPanel(left)
        self._table_selector.grid(row=3, column=0, sticky="ew", pady=(2, 2))

        ctk.CTkLabel(left, text="Generated SQL", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=4, column=0, sticky="w", pady=(8, 4)
        )
        self._sql_box = ctk.CTkTextbox(left, height=72)
        self._sql_box.grid(row=5, column=0, sticky="new", pady=(0, 4))
        self._sql_box.configure(state="disabled")

        self._validation_label = ctk.CTkLabel(left, text="", anchor="w")
        self._validation_label.grid(row=6, column=0, sticky="ew", pady=(0, 4))

        self._results = ResultsTable(left)
        self._results.grid(row=7, column=0, sticky="nsew", pady=(4, 0))

        self._activity = ActivityLogPanel(parent)
        self._activity.grid(row=0, column=1, sticky="nsew", padx=(4, 4), pady=4)

    def _build_stub_tab(self, parent, title: str, message: str) -> None:
        ctk.CTkLabel(parent, text=title, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=12, pady=12)
        ctk.CTkLabel(parent, text=message, wraplength=700, justify="left").pack(anchor="w", padx=12, pady=4)

    def _build_docs_tab(self, parent) -> None:
        docs = ctk.CTkTextbox(parent, wrap="word")
        docs.pack(fill="both", expand=True, padx=12, pady=12)
        docs.insert(
            "1.0",
            """Text-to-SQL workflow

1. Open Settings and configure a PostgreSQL connection plus the FastAPI endpoint.
2. Ask a natural language question on the Text-to-SQL tab.
3. Click Execute — the tool loads schema and suggests relevant tables.
4. Review or adjust the table selection, then click Run Query.
5. Generated SQL appears before execution; validation and results follow.

Safety rules
• Only SELECT and WITH queries are executed.
• INSERT, UPDATE, DELETE, DROP, ALTER, and multi-statement batches are blocked.
• Results are view-only.

Activity log
• Summary view shows high-level pipeline events.
• Toggle Details for structured payloads.

Table selection is locked once SQL generation starts; changing tables after
that has no effect on the current run.
""",
        )
        docs.configure(state="disabled")

    def _open_settings(self) -> None:
        SettingsWindow(self, self.app_state, on_saved=self._on_settings_saved)

    def _on_settings_saved(self) -> None:
        self.app_state.load_settings()
        self._pipeline = Text2SqlPipeline(settings=self.app_state.settings)
        self._adapters = build_adapters(pipeline=self._pipeline)
        self.adapter = self._adapters["Text-to-SQL"]
        self._reset_run_state()
        self._refresh_connection_label()
        self._set_status("Settings saved.")

    def _on_query_changed(self) -> None:
        query = self._query_box.get("1.0", "end").strip()
        if self._run_locked:
            return
        if self._awaiting_table_confirm and self._prepare_result is not None:
            if query == self._prepare_result.question:
                return
        if query != self._last_query:
            self._prepare_result = None
            self._awaiting_table_confirm = False
            self._execute_btn.configure(text="Execute")

    def _reset_run_state(self) -> None:
        self._prepare_result = None
        self._awaiting_table_confirm = False
        self._run_locked = False
        self._execute_btn.configure(text="Execute", state="normal")

    def _on_clear(self) -> None:
        self.app_state.clear_query(clear_log=True)
        self._query_box.delete("1.0", "end")
        self._last_query = ""
        self._set_sql_text("")
        self._validation_label.configure(text="")
        self._set_status("")
        self._results.render(None)
        self._activity.clear()
        self._table_selector.clear()
        self._reset_run_state()

    def _set_sql_text(self, text: str) -> None:
        self._sql_box.configure(state="normal")
        self._sql_box.delete("1.0", "end")
        if text:
            self._sql_box.insert("1.0", text)
        self._sql_box.configure(state="disabled")

    def _set_status(self, text: str, *, error: bool = False) -> None:
        color = "#e74c3c" if error else "gray"
        self._status_label.configure(text=text, text_color=color)

    def _on_execute(self) -> None:
        query = self._query_box.get("1.0", "end").strip()
        if not query:
            self._set_status("Enter a natural language question first.", error=True)
            return

        if self._run_locked:
            return

        if self._awaiting_table_confirm and self._prepare_result is not None:
            self._start_run_query(query)
            return

        self._last_query = query
        self.app_state.logger.clear()
        self.app_state.clear_query(clear_log=False)
        self._activity.clear()
        self._set_sql_text("")
        self._validation_label.configure(text="")
        self._results.render(None)
        self._table_selector.clear()
        self._prepare_result = None
        self._awaiting_table_confirm = False

        self._set_status("Loading schema and selecting tables…")
        self._execute_btn.configure(state="disabled", text="Loading…")

        def worker():
            def on_event(event: ActivityEvent) -> None:
                self.after(0, lambda e=event: self._on_pipeline_event(e))

            self.app_state.logger.set_listener(on_event)
            try:
                self.adapter.pipeline.settings = self.app_state.settings or self.app_state.load_settings()
                result = self.adapter.prepare(query, logger=self.app_state.logger)
                self.after(0, lambda: self._on_prepare_done(query, result))
            except Exception as exc:
                self.after(0, lambda: self._on_execute_error(str(exc)))
            finally:
                self.after(0, lambda: self.app_state.logger.set_listener(None))

        threading.Thread(target=worker, daemon=True).start()

    def _on_prepare_done(self, query: str, result) -> None:
        from tool.adapters.base import ExecuteResult

        if isinstance(result, ExecuteResult):
            self._execute_btn.configure(state="normal", text="Execute")
            self._set_status(result.error or "Preparation failed", error=True)
            if result.error:
                messagebox.showerror("Prepare failed", result.error)
            return

        suggested = [t.name for t in result.selection.selected]
        self._prepare_result = result
        self._awaiting_table_confirm = True
        self._last_query = result.question
        self._table_selector.set_tables(result.all_tables, suggested, result.selection.scores)
        self._execute_btn.configure(state="normal", text="Run Query")
        self._set_status(
            f"{len(suggested)} tables ready ({', '.join(suggested[:4])}{'…' if len(suggested) > 4 else ''}) — click Run Query."
        )

    def _start_run_query(self, query: str) -> None:
        if self._prepare_result is None:
            self._set_status("Run Execute first to load schema tables.", error=True)
            return

        prepare = self._prepare_result
        selected = self._table_selector.get_selected()
        if not selected:
            selected = [t.name for t in prepare.selection.selected]
        if not selected:
            self._set_status("Select at least one table before running.", error=True)
            return

        run_query = prepare.question
        self._awaiting_table_confirm = False
        self._run_locked = True
        self._table_selector.lock()
        self._execute_btn.configure(state="disabled", text="Running…")
        self._set_status(f"Generating SQL using {len(selected)} tables…")

        def worker():
            def on_event(event: ActivityEvent) -> None:
                self.after(0, lambda e=event: self._on_pipeline_event(e))

            self.app_state.logger.set_listener(on_event)
            try:
                self.adapter.pipeline.settings = self.app_state.settings or self.app_state.load_settings()
                result = self.adapter.execute_with_tables(
                    run_query,
                    prepare,
                    selected,
                    logger=self.app_state.logger,
                )
                self.after(0, lambda: self._on_execute_done(result))
            except Exception as exc:
                self.after(0, lambda: self._on_execute_error(str(exc)))
            finally:
                self.after(0, lambda: self.app_state.logger.set_listener(None))

        threading.Thread(target=worker, daemon=True).start()

    def _on_pipeline_event(self, event: ActivityEvent) -> None:
        self._activity.append_event(event)

        if event.event == "sql_generated":
            sql = event.details.get("sql")
            if sql:
                self._set_sql_text(sql)
                self._set_status("SQL generated — validating and executing…")
        elif event.event == "validation_start":
            self._set_status("Validating SQL…")
        elif event.event == "validation_passed":
            self._validation_label.configure(text="Validation passed", text_color="#2ecc71")
        elif event.event == "validation_failed":
            self._validation_label.configure(text=event.message, text_color="#e74c3c")
        elif event.event == "executing":
            self._set_status("Executing query…")

    def _on_execute_done(self, result) -> None:
        self._execute_btn.configure(state="normal", text="Execute")
        self._run_locked = False
        self._prepare_result = None
        self.app_state.apply_result(result)

        if result.generated_sql:
            self._set_sql_text(result.generated_sql)

        if result.validation_status:
            v = result.validation_status
            if v.get("passed"):
                self._validation_label.configure(text=v.get("message", "Validation passed"), text_color="#2ecc71")
            else:
                self._validation_label.configure(text=v.get("message", "Validation failed"), text_color="#e74c3c")
        elif result.error and result.generated_sql:
            self._validation_label.configure(text="", text_color="gray")

        self._results.render(result.result_df, result.result_meta, result.selected_tables)

        if result.success:
            self._set_status(
                f"Done — {result.result_meta.get('row_count', 0)} rows in {result.result_meta.get('duration_ms', '?')} ms"
            )
        elif result.validation_status and not result.validation_status.get("passed"):
            self._set_status(result.error or "Validation failed", error=True)
        elif result.error:
            self._set_status(result.error, error=True)
            if not result.generated_sql:
                messagebox.showerror("Execute failed", result.error)

    def _on_execute_error(self, error: str) -> None:
        self._execute_btn.configure(state="normal", text="Execute")
        self._run_locked = False
        self._prepare_result = None
        self._set_status(error, error=True)
        messagebox.showerror("Execute failed", error)


def run_desktop() -> None:
    app = MainWindow()
    app.mainloop()
