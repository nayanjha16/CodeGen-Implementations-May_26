"""Serving layer for the model UI — one-shot inference behind the web app.

This wraps the *exact* two-stage inference path from
``run_multi_task_inference.py`` (Stage A draft → Stage B revise) so the FastAPI
app stays thin and no inference logic is duplicated or re-derived. It exposes two
supported tasks for the UI — ``text2sql`` (NL → SQL) and ``sql2nosql`` (SQL →
MongoDB MQL) — running the accepted **Run #2 teacher** adapter (two-stage), the
project's final version (STATUS.md).

Design points:
- The model + tokenizer load **once** at process start (``ModelService`` is a
  singleton held by the app) and are reused for every request — loading the
  1.5B base + LoRA per request would be unusably slow.
- A request supplies ``(task, db_id, user_input)``. The schema for ``db_id`` is
  looked up from the same compact schema maps the pipeline uses
  (``loader.load_sql_schema_map`` / ``load_nosql_schema_map``), and a throwaway
  ``Example`` is built so ``prompt_builder`` / ``generator`` behave identically
  to evaluation. There is no gold and no ``correct`` flag here — this is live
  inference, not scored eval.
- Execution is optional per call. When on, the generated query runs against the
  real DB via the pipeline's own harnesses (``sql_exec`` / ``mongo_exec``) and
  the resulting rows are returned for display. Execution errors are captured and
  surfaced, never raised to the caller.
"""

from __future__ import annotations

import logging
import threading
import time

from . import config, loader
from . import model_factory as mf
from . import mongo_exec, sql_exec
from .device import describe, enable_mps_cpu_fallback, get_device
from .generator import generate_and_extract
from .prompt_builder import build_prompt

log = logging.getLogger(__name__)

# Tasks the UI serves — all three the project trains.
SUPPORTED_TASKS = ("text2sql", "sql2nosql", "text2nosql")

# Human-facing labels for the UI (kept here so the app has a single source).
TASK_LABELS = {
    "text2sql": "Natural language → SQL",
    "sql2nosql": "SQL → MongoDB (MQL)",
    "text2nosql": "Natural language → MongoDB (MQL)",
}

# What the user types for each task, and which engine executes the output.
TASK_INPUT_KIND = {"text2sql": "question", "sql2nosql": "sql", "text2nosql": "question"}
TASK_ENGINE = {"text2sql": "sqlite", "sql2nosql": "mongosh", "text2nosql": "mongosh"}


class ModelService:
    """Loads the Run #2 teacher adapter once; serves two-stage inference.

    Thread-safe: HTTP requests may arrive concurrently, but a single model on one
    device cannot decode two batches at once safely, so generation is serialised
    with a lock. Inference is the bottleneck regardless, so this is not a real
    throughput limit for a demo/eval UI.
    """

    def __init__(self, arm: str = "teacher") -> None:
        self._arm = arm
        self._lock = threading.Lock()
        self._tokenizer = None
        self._model = None
        self._loaded = False
        self._device_desc = ""

    # --- lifecycle ---------------------------------------------------------
    def load(self) -> None:
        """Load tokenizer + adapter onto the resolved device (idempotent)."""
        if self._loaded:
            return
        enable_mps_cpu_fallback()
        self._device_desc = describe()
        log.info("serving startup: %s", self._device_desc)

        from run_multi_task_inference import ARMS  # arm → (ckpt dir, two_stage)

        ckpt, two_stage = ARMS[self._arm]
        if not two_stage:
            raise ValueError(f"UI serves two-stage arms only; {self._arm!r} is draft-only")
        if not ckpt.exists():
            raise FileNotFoundError(
                f"adapter for arm {self._arm!r} missing: {ckpt}. "
                "Copy the trained Run #2 adapter to this path before serving."
            )
        self._tokenizer = mf.load_tokenizer()
        self._model = mf.load_adapter(ckpt, trainable=False)
        self._loaded = True
        log.info("serving ready: arm=%s ckpt=%s device=%s",
                 self._arm, ckpt, get_device().type)

    @property
    def ready(self) -> bool:
        return self._loaded

    @property
    def device_description(self) -> str:
        return self._device_desc or describe()

    # --- schema / databases ------------------------------------------------
    @staticmethod
    def databases(task: str) -> list[str]:
        """Sorted db_ids available for a task (drives the UI dropdown)."""
        _check_task(task)
        schema_map = _schema_map_for(task)
        return sorted(schema_map)

    @staticmethod
    def schema_for(task: str, db_id: str) -> str:
        """Compact schema string for a db_id, or raise KeyError if unknown."""
        _check_task(task)
        schema_map = _schema_map_for(task)
        if db_id not in schema_map:
            raise KeyError(f"unknown db_id {db_id!r} for task {task!r}")
        return schema_map[db_id]

    # --- inference ---------------------------------------------------------
    def generate(self, task: str, db_id: str | None, user_input: str,
                 execute: bool = True, schema: str | None = None) -> dict:
        """Run two-stage inference for one input; optionally execute the result.

        Two schema sources:
        - a bundled ``db_id`` (schema looked up from the pipeline's maps) — the
          only path that can *execute*, since execution needs a real local DB;
        - a pasted ``schema`` string (``db_id`` optional/ignored) — **generate
          only**, execution is force-disabled because there is no DB to run against.

        Returns a JSON-ready dict with the draft, the Stage-B analysis, the final
        query, and — when executed — the rows or the error.
        """
        _check_task(task)
        if not self._loaded:
            raise RuntimeError("model not loaded; call load() first")
        user_input = (user_input or "").strip()
        if not user_input:
            raise ValueError("empty input")

        custom_schema = bool(schema and schema.strip())
        if custom_schema:
            schema = schema.strip()
            db_id = db_id or "(custom)"
            execute = False  # no real DB behind a pasted schema
        else:
            if not db_id:
                raise ValueError("db_id required unless a custom schema is provided")
            schema = self.schema_for(task, db_id)  # raises KeyError on bad db_id

        example = _make_example(task, db_id, user_input, schema)

        t0 = time.time()
        with self._lock:  # one decode at a time on a single device
            # Stage A — draft (no reference / RAG in the UI path; the model's
            # 20% no-reference training keeps this in-distribution).
            draft = generate_and_extract(self._model, self._tokenizer,
                                         [build_prompt(example)], task)[0][1]
            # Stage B — revise, conditioned on the model's own draft.
            analysis, final_query = generate_and_extract(
                self._model, self._tokenizer,
                [build_prompt(example, broken_draft=draft)], task)[0]
        gen_ms = int((time.time() - t0) * 1000)

        result = {
            "task": task,
            "db_id": db_id,
            "input": user_input,
            "schema": schema,
            "draft": draft,
            "analysis": analysis,
            "final_query": final_query,
            "engine": TASK_ENGINE[task],
            "generation_ms": gen_ms,
            "custom_schema": custom_schema,
            "executed": False,
            "execution": None,
        }
        if execute:
            result["executed"] = True
            result["execution"] = _execute(task, db_id, final_query)
        return result


# --- module helpers --------------------------------------------------------
def _check_task(task: str) -> None:
    if task not in SUPPORTED_TASKS:
        raise ValueError(
            f"unsupported task {task!r}; UI serves {SUPPORTED_TASKS}")


def _schema_map_for(task: str) -> dict[str, str]:
    return (loader.load_sql_schema_map() if task == "text2sql"
            else loader.load_nosql_schema_map())


def _make_example(task: str, db_id: str, user_input: str, schema: str) -> loader.Example:
    """Build a throwaway Example for live inference (no gold, no split).

    For ``text2sql`` the input is the NL question; for ``sql2nosql`` it is the
    source SQL. ``gold`` is unused by the drafting/revising prompts, so a marker
    string is fine — it never reaches the model or the executor.
    """
    is_sql_input = task == "sql2nosql"
    return loader.Example(
        task=task,
        source="spider" if task == "text2sql" else "docspider",
        split="serve",
        db_id=db_id,
        question=None if is_sql_input else user_input,
        source_sql=user_input if is_sql_input else None,
        gold="",              # not used at inference time
        schema=schema,
        difficulty=None,
        origin_index=-1,
        aux_sql=None,
    )


def _execute(task: str, db_id: str, query: str) -> dict:
    """Execute a generated query against the real DB; return a JSON-ready dict.

    Reuses the pipeline harnesses (``sql_exec`` / ``mongo_exec``) so what the UI
    runs is identical to what the eval metric runs. Failures are captured, not
    raised — a broken generated query is a normal, displayable outcome.
    """
    try:
        if task == "text2sql":
            res = sql_exec.run_sql(db_id, query)
            columns = None  # run_sql returns row-tuples without column names
        else:
            res = mongo_exec.run_mql(db_id, query)
            columns = None
    except RuntimeError as e:  # e.g. mongosh not on PATH
        return {"ok": False, "error": str(e), "rows": None, "row_count": 0,
                "truncated": False, "columns": None}

    rows = res.rows if res.ok and res.rows is not None else []
    truncated = len(rows) > _MAX_DISPLAY_ROWS
    return {
        "ok": res.ok,
        "error": res.error,
        "rows": rows[:_MAX_DISPLAY_ROWS],
        "row_count": len(rows),
        "truncated": truncated,
        "columns": columns,
    }


_MAX_DISPLAY_ROWS = 200  # cap payload size; UI notes when truncated
