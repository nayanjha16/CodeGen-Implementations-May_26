"""
RepoCoder Studio — Inference API

FastAPI replacement for the notebook's interactive Gradio demo (Combined Stage,
Cell 25). Serves the baseline (pretrained) and fine-tuned (LoRA) student model for
the six supervised tasks defined in src.registry.TaskRegistry.

Corpus building, validation, and training are intentionally out of scope here —
those remain offline notebook/CLI steps. This app only loads already-trained
artifacts and serves generation requests.
"""

from __future__ import annotations

import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from src.config import CONFIG
from src.generation_engine import GenerationEngine
from src.logger import LOG
from src.registry import TaskRegistry

from app.schemas import (
    CompareRequest,
    CompareResponse,
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
    TaskInfo,
)

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = GenerationEngine(CONFIG)

    LOG.info("Loading baseline model...")
    baseline_model, baseline_tokenizer = engine.load_model("baseline")

    finetuned_model = None
    finetuned_tokenizer = None
    finetuned_error = None
    try:
        LOG.info("Loading fine-tuned (LoRA) model...")
        finetuned_model, finetuned_tokenizer = engine.load_model("finetuned")
    except Exception as exc:
        # Covers a missing adapter directory as well as an incomplete/corrupt one
        # (e.g. unresolved git-lfs pointer stubs instead of real JSON/tensor files).
        # Either way the server should still come up and serve baseline-only.
        finetuned_error = str(exc)
        LOG.warning(f"Fine-tuned adapter unavailable, continuing without it: {exc}")

    app.state.engine = engine
    app.state.task_registry = TaskRegistry()
    app.state.models = {
        "baseline": (baseline_model, baseline_tokenizer),
        "finetuned": (finetuned_model, finetuned_tokenizer) if finetuned_model else None,
    }
    app.state.finetuned_error = finetuned_error
    app.state.locks = {
        "baseline": threading.Lock(),
        "finetuned": threading.Lock(),
    }

    LOG.info("RepoCoder Studio inference API ready.")
    yield


app = FastAPI(
    title="RepoCoder Studio — Inference API",
    version=CONFIG.experiment.experiment_version,
    lifespan=lifespan,
)


def _device_label() -> str:
    import torch

    return "cuda" if torch.cuda.is_available() else "cpu"


def _run_generation(model_type: str, task_id: str, input_text: str) -> str:
    entry = app.state.models.get(model_type)
    if entry is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model '{model_type}' is not loaded on this server.",
        )
    model, tokenizer = entry
    engine: GenerationEngine = app.state.engine
    instruction = engine.prompt_builder.build_instruction(task_id)
    with app.state.locks[model_type]:
        return engine.generate(model, tokenizer, instruction, input_text or "", task_id=task_id)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        device=_device_label(),
        baseline_loaded=app.state.models.get("baseline") is not None,
        finetuned_loaded=app.state.models.get("finetuned") is not None,
        finetuned_error=app.state.finetuned_error,
    )


@app.get("/api/tasks", response_model=list[TaskInfo])
def list_tasks() -> list[TaskInfo]:
    registry: TaskRegistry = app.state.task_registry
    return [
        TaskInfo(task_id=task_id, **info)
        for task_id, info in registry.all_tasks().items()
    ]


@app.post("/api/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    registry: TaskRegistry = app.state.task_registry
    if request.task_id not in registry.all_tasks():
        raise HTTPException(status_code=404, detail=f"Unknown task_id: {request.task_id}")
    output = _run_generation(request.model_type, request.task_id, request.input_text)
    return GenerateResponse(task_id=request.task_id, model_type=request.model_type, output=output)


@app.post("/api/compare", response_model=CompareResponse)
def compare(request: CompareRequest) -> CompareResponse:
    registry: TaskRegistry = app.state.task_registry
    if request.task_id not in registry.all_tasks():
        raise HTTPException(status_code=404, detail=f"Unknown task_id: {request.task_id}")

    baseline_output = _run_generation("baseline", request.task_id, request.input_text)

    finetuned_available = app.state.models.get("finetuned") is not None
    finetuned_output = (
        _run_generation("finetuned", request.task_id, request.input_text)
        if finetuned_available
        else None
    )

    return CompareResponse(
        task_id=request.task_id,
        baseline_output=baseline_output,
        finetuned_output=finetuned_output,
        finetuned_available=finetuned_available,
    )


app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
