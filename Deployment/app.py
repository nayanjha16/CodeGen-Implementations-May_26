"""FastAPI app to run the model UI for text2sql and sql2nosql (SPEC/STATUS: Run #2).

A thin HTTP layer over ``src.serving.ModelService``. It serves a single-page UI
(``static/index.html``) and a small JSON API:

    GET  /health                     — liveness + whether the model is loaded
    GET  /api/tasks                  — the two supported tasks + labels
    GET  /api/databases?task=...     — db_ids for the task's dropdown
    GET  /api/schema?task=&db_id=    — compact schema for a chosen db (preview)
    POST /api/generate               — two-stage inference (+ optional execution)

The heavy model load happens once, lazily on first need (and eagerly at startup
unless ``CODEGEN_LAZY_LOAD=1``), so requests after warm-up are just inference.

Run locally:
    uvicorn app:app --host 0.0.0.0 --port 8000
Or:
    python app.py            # same, convenience wrapper
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.logger import setup_logging
from src.serving import SUPPORTED_TASKS, TASK_INPUT_KIND, TASK_LABELS, ModelService

log = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parent / "static"
ARM = os.environ.get("CODEGEN_ARM", "teacher")  # Run #2 final = teacher
LAZY_LOAD = os.environ.get("CODEGEN_LAZY_LOAD") == "1"

service = ModelService(arm=ARM)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    setup_logging("serve_app")
    if not LAZY_LOAD:
        try:
            service.load()
        except Exception:  # don't kill the server; /health will report not-ready
            log.exception("eager model load failed; will retry on first request")
    yield


app = FastAPI(title="Codegen-phase2 — Query Translator", lifespan=lifespan)


# --- request/response models ----------------------------------------------
class GenerateRequest(BaseModel):
    # allow the JSON key "schema" while avoiding the BaseModel.schema shadow.
    model_config = {"populate_by_name": True}

    task: str = Field(..., description="text2sql | sql2nosql | text2nosql")
    db_id: str | None = Field(None, description="a database id from /api/databases (omit if using a custom schema)")
    input: str = Field(..., description="NL question or SQL, per the task")
    execute: bool = Field(True, description="run the generated query against the DB (ignored for custom schema)")
    custom_schema: str | None = Field(
        None, alias="schema",
        description="paste a custom schema for generate-only (no execution)")


# --- helpers ---------------------------------------------------------------
def _ensure_loaded() -> None:
    """Load the model on demand; convert failures into a 503."""
    if service.ready:
        return
    try:
        service.load()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"model unavailable: {e}") from e
    except Exception as e:  # noqa: BLE001 — surface any load failure as 503
        raise HTTPException(status_code=503, detail=f"model load failed: {e}") from e


# --- routes ----------------------------------------------------------------
@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "model_loaded": service.ready,
        "arm": ARM,
        "device": service.device_description,
        "supported_tasks": list(SUPPORTED_TASKS),
    }


@app.get("/api/tasks")
def tasks() -> dict:
    return {
        "tasks": [
            {"id": t, "label": TASK_LABELS[t], "input_kind": TASK_INPUT_KIND[t]}
            for t in SUPPORTED_TASKS
        ]
    }


@app.get("/api/databases")
def databases(task: str) -> dict:
    if task not in SUPPORTED_TASKS:
        raise HTTPException(status_code=400, detail=f"unsupported task {task!r}")
    return {"task": task, "databases": ModelService.databases(task)}


@app.get("/api/schema")
def schema(task: str, db_id: str) -> dict:
    if task not in SUPPORTED_TASKS:
        raise HTTPException(status_code=400, detail=f"unsupported task {task!r}")
    try:
        return {"task": task, "db_id": db_id, "schema": ModelService.schema_for(task, db_id)}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@app.post("/api/generate")
def generate(req: GenerateRequest) -> dict:
    if req.task not in SUPPORTED_TASKS:
        raise HTTPException(status_code=400, detail=f"unsupported task {req.task!r}")
    _ensure_loaded()
    try:
        return service.generate(req.task, req.db_id, req.input,
                                execute=req.execute, schema=req.custom_schema)
    except KeyError as e:  # unknown db_id
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValueError as e:  # empty input / missing db_id, etc.
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


# Static assets (CSS/JS live inline in index.html, but mount for future assets).
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "8000")),
        reload=False,
    )
