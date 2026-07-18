"""Settings dialog — database, FastAPI, schema selection."""

from __future__ import annotations

import uuid
from typing import Callable

import customtkinter as ctk
from tkinter import messagebox

from tool.core.connection_tester import run_database_test, run_fastapi_test, run_mongo_test
from tool.core.settings_store import (
    AppSettings,
    DatabaseConnection,
    ExecutionSettings,
    FastApiSettings,
    MongoConnection,
    SchemaSelectionSettings,
    SettingsStore,
)
from tool.desktop.app_state import AppState


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master, state: AppState, on_saved: Callable[[], None] | None = None):
        super().__init__(master)
        self.title("Settings")
        self.geometry("720x640")
        self.app_state = state
        self.on_saved = on_saved
        self.store = SettingsStore()
        self.settings = self.store.load()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self,
            text="Configure PostgreSQL, MongoDB, and FastAPI inference",
            font=ctk.CTkFont(size=13),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))

        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        self.tabs.add("Database")
        self.tabs.add("MongoDB")
        self.tabs.add("FastAPI")
        self.tabs.add("Schema")

        self._build_database_tab(self.tabs.tab("Database"))
        self._build_mongo_tab(self.tabs.tab("MongoDB"))
        self._build_fastapi_tab(self.tabs.tab("FastAPI"))
        self._build_schema_tab(self.tabs.tab("Schema"))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="e", padx=16, pady=(0, 12))
        ctk.CTkButton(btn_row, text="Close", command=self.destroy, width=100).pack(side="right")

        self.transient(master)
        self.grab_set()

    def _notify_saved(self) -> None:
        self.settings = self.store.load()
        self.app_state.settings = self.settings
        if self.on_saved:
            self.on_saved()

    # --- Database tab ---

    def _build_database_tab(self, parent) -> None:
        parent.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(parent, text="Active connection").grid(row=0, column=0, sticky="w", padx=8, pady=(8, 2))
        names = [c.name for c in self.settings.connections]
        self._active_var = ctk.StringVar(value=self._active_name())
        self._active_menu = ctk.CTkOptionMenu(
            parent,
            values=names or ["— none —"],
            variable=self._active_var,
            command=self._set_active_connection,
        )
        self._active_menu.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

        self._conn_list = ctk.CTkScrollableFrame(parent, label_text="Connections")
        self._conn_list.grid(row=2, column=0, sticky="nsew", padx=8, pady=4)
        parent.grid_rowconfigure(2, weight=1)
        self._refresh_connection_list()

        add = ctk.CTkFrame(parent)
        add.grid(row=3, column=0, sticky="ew", padx=8, pady=8)
        add.grid_columnconfigure((0, 1), weight=1)

        self._new_name = ctk.CTkEntry(add, placeholder_text="Name")
        self._new_host = ctk.CTkEntry(add, placeholder_text="Host (localhost)")
        self._new_port = ctk.CTkEntry(add, placeholder_text="Port (5432)")
        self._new_db = ctk.CTkEntry(add, placeholder_text="Database")
        self._new_user = ctk.CTkEntry(add, placeholder_text="Username")
        self._new_pwd = ctk.CTkEntry(add, placeholder_text="Password", show="*")

        self._new_name.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        self._new_host.grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        self._new_port.grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        self._new_db.grid(row=1, column=1, padx=4, pady=4, sticky="ew")
        self._new_user.grid(row=2, column=0, padx=4, pady=4, sticky="ew")
        self._new_pwd.grid(row=2, column=1, padx=4, pady=4, sticky="ew")
        ctk.CTkButton(add, text="Add connection", command=self._add_connection).grid(
            row=3, column=0, columnspan=2, padx=4, pady=8, sticky="ew"
        )

    def _active_name(self) -> str:
        conn = self.settings.get_active_connection()
        return conn.name if conn else "— none —"

    def _set_active_connection(self, name: str) -> None:
        if name == "— none —":
            self.settings.active_connection_id = None
        else:
            for c in self.settings.connections:
                if c.name == name:
                    self.settings.active_connection_id = c.id
                    break
        self.store.save(self.settings)
        self._notify_saved()

    def _refresh_connection_list(self) -> None:
        for w in self._conn_list.winfo_children():
            w.destroy()
        for conn in self.settings.connections:
            row = ctk.CTkFrame(self._conn_list)
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(
                row,
                text=f"{conn.name}  ·  {conn.host}:{conn.port}/{conn.database}",
                anchor="w",
            ).pack(side="left", fill="x", expand=True, padx=8, pady=6)
            ctk.CTkButton(row, text="Test", width=60, command=lambda c=conn: self._test_connection(c)).pack(
                side="right", padx=4, pady=4
            )
            ctk.CTkButton(row, text="Delete", width=60, fg_color="#8b0000", command=lambda c=conn: self._delete_connection(c)).pack(
                side="right", padx=4, pady=4
            )

        names = [c.name for c in self.settings.connections] or ["— none —"]
        self._active_menu.configure(values=names)
        self._active_var.set(self._active_name())

    def _add_connection(self) -> None:
        name = self._new_name.get().strip()
        host = self._new_host.get().strip() or "localhost"
        port_s = self._new_port.get().strip() or "5432"
        database = self._new_db.get().strip()
        if not name or not database:
            messagebox.showwarning("Missing fields", "Name and database are required.")
            return
        conn = DatabaseConnection(
            id=str(uuid.uuid4()),
            name=name,
            host=host,
            port=int(port_s),
            database=database,
            username=self._new_user.get().strip() or "postgres",
            password=self._new_pwd.get(),
        )
        self.store.add_connection(self.settings, conn)
        self._refresh_connection_list()
        self._notify_saved()
        for entry in (self._new_name, self._new_host, self._new_port, self._new_db, self._new_user, self._new_pwd):
            entry.delete(0, "end")

    def _delete_connection(self, conn: DatabaseConnection) -> None:
        if messagebox.askyesno("Delete connection", f"Delete '{conn.name}'?"):
            self.store.delete_connection(self.settings, conn.id)
            self._refresh_connection_list()
            self._notify_saved()

    def _test_connection(self, conn: DatabaseConnection) -> None:
        result = run_database_test(conn, logger=self.app_state.logger)
        if result.success:
            messagebox.showinfo("Connection OK", f"Connected in {result.latency_ms:.0f} ms")
        else:
            messagebox.showerror("Connection failed", result.error or "Unknown error")

    # --- MongoDB tab ---

    def _build_mongo_tab(self, parent) -> None:
        parent.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(parent, text="Active MongoDB connection").grid(row=0, column=0, sticky="w", padx=8, pady=(8, 2))
        names = [c.name for c in self.settings.mongo_connections]
        self._mongo_active_var = ctk.StringVar(value=self._active_mongo_name())
        self._mongo_active_menu = ctk.CTkOptionMenu(
            parent,
            values=names or ["— none —"],
            variable=self._mongo_active_var,
            command=self._set_active_mongo_connection,
        )
        self._mongo_active_menu.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

        self._mongo_conn_list = ctk.CTkScrollableFrame(parent, label_text="MongoDB connections")
        self._mongo_conn_list.grid(row=2, column=0, sticky="nsew", padx=8, pady=4)
        parent.grid_rowconfigure(2, weight=1)
        self._refresh_mongo_connection_list()

        add = ctk.CTkFrame(parent)
        add.grid(row=3, column=0, sticky="ew", padx=8, pady=8)
        add.grid_columnconfigure((0, 1), weight=1)

        self._mongo_new_name = ctk.CTkEntry(add, placeholder_text="Name")
        self._mongo_new_host = ctk.CTkEntry(add, placeholder_text="Host (localhost)")
        self._mongo_new_port = ctk.CTkEntry(add, placeholder_text="Port (27017)")
        self._mongo_new_db = ctk.CTkEntry(add, placeholder_text="Database (dvd)")
        self._mongo_new_user = ctk.CTkEntry(add, placeholder_text="Username")
        self._mongo_new_pwd = ctk.CTkEntry(add, placeholder_text="Password", show="*")
        self._mongo_new_auth = ctk.CTkEntry(add, placeholder_text="Auth source (admin)")

        self._mongo_new_name.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        self._mongo_new_host.grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        self._mongo_new_port.grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        self._mongo_new_db.grid(row=1, column=1, padx=4, pady=4, sticky="ew")
        self._mongo_new_user.grid(row=2, column=0, padx=4, pady=4, sticky="ew")
        self._mongo_new_pwd.grid(row=2, column=1, padx=4, pady=4, sticky="ew")
        self._mongo_new_auth.grid(row=3, column=0, columnspan=2, padx=4, pady=4, sticky="ew")
        ctk.CTkButton(add, text="Add MongoDB connection", command=self._add_mongo_connection).grid(
            row=4, column=0, columnspan=2, padx=4, pady=8, sticky="ew"
        )

    def _active_mongo_name(self) -> str:
        conn = self.settings.get_active_mongo_connection()
        return conn.name if conn else "— none —"

    def _set_active_mongo_connection(self, name: str) -> None:
        if name == "— none —":
            self.settings.active_mongo_connection_id = None
        else:
            for c in self.settings.mongo_connections:
                if c.name == name:
                    self.settings.active_mongo_connection_id = c.id
                    break
        self.store.save(self.settings)
        self._notify_saved()

    def _refresh_mongo_connection_list(self) -> None:
        for w in self._mongo_conn_list.winfo_children():
            w.destroy()
        for conn in self.settings.mongo_connections:
            row = ctk.CTkFrame(self._mongo_conn_list)
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(
                row,
                text=f"{conn.name}  ·  {conn.host}:{conn.port}/{conn.database}",
                anchor="w",
            ).pack(side="left", fill="x", expand=True, padx=8, pady=6)
            ctk.CTkButton(row, text="Test", width=60, command=lambda c=conn: self._test_mongo_connection(c)).pack(
                side="right", padx=4, pady=4
            )
            ctk.CTkButton(
                row,
                text="Delete",
                width=60,
                fg_color="#8b0000",
                command=lambda c=conn: self._delete_mongo_connection(c),
            ).pack(side="right", padx=4, pady=4)

        names = [c.name for c in self.settings.mongo_connections] or ["— none —"]
        self._mongo_active_menu.configure(values=names)
        self._mongo_active_var.set(self._active_mongo_name())

    def _add_mongo_connection(self) -> None:
        name = self._mongo_new_name.get().strip()
        host = self._mongo_new_host.get().strip() or "localhost"
        port_s = self._mongo_new_port.get().strip() or "27017"
        database = self._mongo_new_db.get().strip()
        if not name or not database:
            messagebox.showwarning("Missing fields", "Name and database are required.")
            return
        conn = MongoConnection(
            id=str(uuid.uuid4()),
            name=name,
            host=host,
            port=int(port_s),
            database=database,
            username=self._mongo_new_user.get().strip() or "tend",
            password=self._mongo_new_pwd.get(),
            auth_source=self._mongo_new_auth.get().strip() or "admin",
        )
        self.store.add_mongo_connection(self.settings, conn)
        self._refresh_mongo_connection_list()
        self._notify_saved()
        for entry in (
            self._mongo_new_name,
            self._mongo_new_host,
            self._mongo_new_port,
            self._mongo_new_db,
            self._mongo_new_user,
            self._mongo_new_pwd,
            self._mongo_new_auth,
        ):
            entry.delete(0, "end")

    def _delete_mongo_connection(self, conn: MongoConnection) -> None:
        if messagebox.askyesno("Delete connection", f"Delete '{conn.name}'?"):
            self.store.delete_mongo_connection(self.settings, conn.id)
            self._refresh_mongo_connection_list()
            self._notify_saved()

    def _test_mongo_connection(self, conn: MongoConnection) -> None:
        result = run_mongo_test(conn, logger=self.app_state.logger)
        if result.success:
            messagebox.showinfo("Connection OK", f"Connected in {result.latency_ms:.0f} ms")
        else:
            messagebox.showerror("Connection failed", result.error or "Unknown error")

    # --- FastAPI tab ---

    def _build_fastapi_tab(self, parent) -> None:
        parent.grid_columnconfigure(1, weight=1)
        fa = self.settings.fastapi
        fields = [
            ("Base URL", "base_url", fa.base_url),
            ("Health URL", "health_url", fa.health_url),
            ("Model", "model", fa.model),
            ("Intent", "intent", fa.intent),
            ("API key (optional)", "api_key", fa.api_key),
        ]
        self._fa_entries: dict[str, ctk.CTkEntry] = {}
        for i, (label, key, val) in enumerate(fields):
            ctk.CTkLabel(parent, text=label).grid(row=i, column=0, sticky="w", padx=8, pady=6)
            entry = ctk.CTkEntry(parent, show="*" if key == "api_key" else "")
            entry.insert(0, val)
            entry.grid(row=i, column=1, sticky="ew", padx=8, pady=6)
            self._fa_entries[key] = entry

        ctk.CTkLabel(parent, text="Timeout (sec)").grid(row=len(fields), column=0, sticky="w", padx=8, pady=6)
        self._fa_timeout = ctk.CTkEntry(parent)
        self._fa_timeout.insert(0, str(fa.timeout_sec))
        self._fa_timeout.grid(row=len(fields), column=1, sticky="ew", padx=8, pady=6)

        ctk.CTkLabel(parent, text="Max tokens").grid(row=len(fields) + 1, column=0, sticky="w", padx=8, pady=6)
        self._fa_tokens = ctk.CTkEntry(parent)
        self._fa_tokens.insert(0, str(fa.max_tokens))
        self._fa_tokens.grid(row=len(fields) + 1, column=1, sticky="ew", padx=8, pady=6)

        ctk.CTkLabel(
            parent,
            text="LoRA adapter runs on this server — not loaded locally.",
            text_color="gray",
        ).grid(row=len(fields) + 2, column=0, columnspan=2, sticky="w", padx=8, pady=4)

        btn_row = ctk.CTkFrame(parent, fg_color="transparent")
        btn_row.grid(row=len(fields) + 3, column=0, columnspan=2, sticky="ew", padx=8, pady=12)
        ctk.CTkButton(btn_row, text="Save", command=self._save_fastapi).pack(side="left", padx=4)
        ctk.CTkButton(btn_row, text="Test API", command=self._test_fastapi).pack(side="left", padx=4)

    def _save_fastapi(self) -> None:
        self.settings.fastapi = FastApiSettings(
            base_url=self._fa_entries["base_url"].get().strip(),
            health_url=self._fa_entries["health_url"].get().strip(),
            api_key=self._fa_entries["api_key"].get(),
            model=self._fa_entries["model"].get().strip(),
            intent=self._fa_entries["intent"].get().strip(),
            timeout_sec=int(self._fa_timeout.get() or 60),
            max_tokens=int(self._fa_tokens.get() or 256),
            temperature=self.settings.fastapi.temperature,
        )
        self.store.save(self.settings)
        self._notify_saved()
        messagebox.showinfo("Saved", "FastAPI settings saved.")

    def _test_fastapi(self) -> None:
        cfg = FastApiSettings(
            base_url=self._fa_entries["base_url"].get().strip(),
            health_url=self._fa_entries["health_url"].get().strip(),
            api_key=self._fa_entries["api_key"].get(),
            model=self._fa_entries["model"].get().strip(),
            intent=self._fa_entries["intent"].get().strip(),
            timeout_sec=int(self._fa_timeout.get() or 60),
            max_tokens=int(self._fa_tokens.get() or 256),
        )
        result = run_fastapi_test(cfg, logger=self.app_state.logger)
        if result.success:
            messagebox.showinfo("API OK", f"Health check passed ({result.latency_ms:.0f} ms)")
        else:
            messagebox.showerror("API failed", result.error or "Unknown error")

    # --- Schema tab ---

    def _build_schema_tab(self, parent) -> None:
        parent.grid_columnconfigure(1, weight=1)
        ss = self.settings.schema_selection
        ex = self.settings.execution

        ctk.CTkLabel(parent, text="Embedding model").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self._emb_model = ctk.CTkEntry(parent)
        self._emb_model.insert(0, ss.embedding_model)
        self._emb_model.grid(row=0, column=1, sticky="ew", padx=8, pady=6)

        ctk.CTkLabel(parent, text="Top-K tables").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self._top_k = ctk.CTkEntry(parent)
        self._top_k.insert(0, str(ss.top_k))
        self._top_k.grid(row=1, column=1, sticky="ew", padx=8, pady=6)

        ctk.CTkLabel(parent, text="Min score").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        self._min_score = ctk.CTkEntry(parent)
        self._min_score.insert(0, str(ss.min_score))
        self._min_score.grid(row=2, column=1, sticky="ew", padx=8, pady=6)

        ctk.CTkLabel(parent, text="Max result rows").grid(row=3, column=0, sticky="w", padx=8, pady=6)
        self._max_rows = ctk.CTkEntry(parent)
        self._max_rows.insert(0, str(ex.max_result_rows))
        self._max_rows.grid(row=3, column=1, sticky="ew", padx=8, pady=6)

        ctk.CTkLabel(parent, text="Query timeout (sec)").grid(row=4, column=0, sticky="w", padx=8, pady=6)
        self._query_timeout = ctk.CTkEntry(parent)
        self._query_timeout.insert(0, str(ex.query_timeout_sec))
        self._query_timeout.grid(row=4, column=1, sticky="ew", padx=8, pady=6)

        ctk.CTkButton(parent, text="Save", command=self._save_schema).grid(
            row=5, column=0, columnspan=2, padx=8, pady=16, sticky="ew"
        )

    def _save_schema(self) -> None:
        self.settings.schema_selection = SchemaSelectionSettings(
            embedding_model=self._emb_model.get().strip(),
            top_k=int(self._top_k.get() or 8),
            min_score=float(self._min_score.get() or 0.3),
        )
        self.settings.execution = ExecutionSettings(
            max_result_rows=int(self._max_rows.get() or 1000),
            query_timeout_sec=int(self._query_timeout.get() or 30),
            schema_max_tables=self.settings.execution.schema_max_tables,
        )
        self.store.save(self.settings)
        self._notify_saved()
        messagebox.showinfo("Saved", "Schema and execution settings saved.")
