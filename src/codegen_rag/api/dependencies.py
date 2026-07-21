"""Lazy singleton state for the FastAPI app: model, RAG indexes, LLM client,
and a per-db_id SQL schema cache. Everything heavy (torch, faiss) is imported
inside the getter functions, and every getter is a plain FastAPI dependency,
so tests can override any single one via ``app.dependency_overrides`` without
ever importing torch or downloading a model.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from fastapi import HTTPException, Request

from codegen_rag.config import Settings, load_settings

# Checkpoint directories that `load_model_for_task` should try, per language,
# in preference order (best/most-trained first). Only Rust has an actual
# fine-tuning task in this project (proposal's Task 4, "new language
# extension") -- every other language always serves the base
# `codegen-350M-multi` model, which is what it was already doing.
_FINE_TUNED_CHECKPOINTS: dict[str, tuple[str, ...]] = {
    # Checkpoint 2's full/continued-pretraining run (best) before falling
    # back to Checkpoint 1's smaller LoRA subset run.
    "rust": ("rust_full", "rust_lora_subset"),
}


@dataclass
class AppState:
    settings: Settings | None = None
    model: Any = None
    dense_index: Any = None
    ast_index: Any = None
    llm_client: Any = None
    schema_cache: dict[str, Any] = field(default_factory=dict)
    # Lazily-loaded fine-tuned model variants, keyed by language (e.g. "rust").
    # Kept separate from ``model`` (the base-model singleton) so existing
    # tests/call sites that only ever touch ``state.model`` are unaffected.
    language_models: dict[str, Any] = field(default_factory=dict)
    # Populated the first time each language is resolved, so `/health` and
    # tests can introspect which checkpoint (if any) is actually serving a
    # given language without re-touching disk.
    active_checkpoints: dict[str, str | None] = field(default_factory=dict)


def get_app_state(request: Request) -> AppState:
    if not hasattr(request.app.state, "codegen_state"):
        request.app.state.codegen_state = AppState()
    return request.app.state.codegen_state


def get_settings(state: AppState = None) -> Settings:  # noqa: RUF013 - overridden via Depends at call sites
    if state is None:
        return load_settings()
    if state.settings is None:
        state.settings = load_settings()
    return state.settings


def _is_valid_checkpoint(path: Path) -> bool:
    """A valid checkpoint dir has either `adapter_config.json` (LoRA) or
    `config.json` (full fine-tune) -- an empty/partially-written directory
    (e.g. a Colab disconnect mid-save) has neither."""
    return (path / "adapter_config.json").exists() or (path / "config.json").exists()


def _resolve_run_checkpoint(run_dir: Path) -> Path | None:
    """Resolve one training run's directory (e.g. `checkpoints/rust_full`)
    down to the actual checkpoint to load.

    `CheckpointManager.save()` nests every save under a `checkpoint-NNNNNN`
    subdirectory, not directly in `run_dir` itself, and tracks which one is
    `best` (lowest loss) vs `latest` in `training_state.json`. Preference
    order: the run's own recorded `best` checkpoint, then the
    highest-numbered subdirectory if that state file is missing/unreadable,
    then `run_dir` itself as a last resort (covers any flat/non-nested
    layout that isn't produced by CheckpointManager but is still valid).
    """
    if not run_dir.exists():
        return None

    state_file = run_dir / "training_state.json"
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
            best_dir = state.get("best", {}).get("checkpoint_dir")
            if best_dir and _is_valid_checkpoint(Path(best_dir)):
                return Path(best_dir)
        except (json.JSONDecodeError, OSError):
            pass  # fall through to the directory-listing heuristic below

    subdirs = sorted(
        (d for d in run_dir.glob("checkpoint-*") if d.is_dir()),
        key=lambda d: d.name,
    )
    for candidate in reversed(subdirs):  # highest step number first
        if _is_valid_checkpoint(candidate):
            return candidate

    if _is_valid_checkpoint(run_dir):
        return run_dir

    return None


def _best_checkpoint_dir(settings: Settings, language: str) -> Path | None:
    """Return the best available fine-tuned checkpoint directory for
    ``language``, or ``None`` if this language has no fine-tuning task
    (everything but Rust) or no checkpoint has been trained/saved yet in
    this Drive (e.g. Checkpoint 1/2 haven't been run in this session)."""
    candidates = _FINE_TUNED_CHECKPOINTS.get(language, ())
    if not candidates:
        return None

    checkpoints_root = settings.path_for("checkpoints")
    for name in candidates:
        resolved = _resolve_run_checkpoint(checkpoints_root / name)
        if resolved is not None:
            return resolved
    return None


def describe_available_checkpoints(settings: Settings) -> dict[str, str | None]:
    """Cheap, disk-only check (no model/torch loading) of which fine-tuned
    checkpoint would be selected for each language with a fine-tuning task.
    Used by `/health` so the demo can show "best model" status before any
    generation request has actually triggered a lazy load."""
    return {
        language: (str(path) if (path := _best_checkpoint_dir(settings, language)) else None)
        for language in _FINE_TUNED_CHECKPOINTS
    }


def get_codegen_model(state: AppState, language: str = "python") -> Any:
    """Return the model that should serve ``language``: the best available
    fine-tuned checkpoint if one exists for it, otherwise the shared base
    model singleton (unchanged behavior for every language without a
    fine-tuning task, and for callers that don't pass ``language`` at all).
    """
    language = (language or "python").strip().lower()
    settings = get_settings(state)
    checkpoint_dir = _best_checkpoint_dir(settings, language)

    if checkpoint_dir is None:
        state.active_checkpoints.setdefault(language, None)
        if state.model is None:
            from codegen_rag.models.codegen_wrapper import load_model_for_task

            state.model = load_model_for_task(settings)
        return state.model

    if language not in state.language_models:
        from codegen_rag.models.codegen_wrapper import load_model_for_task

        state.language_models[language] = load_model_for_task(settings, adapter_path=checkpoint_dir)
        state.active_checkpoints[language] = str(checkpoint_dir)
    return state.language_models[language]


def get_rag_indexes(state: AppState) -> tuple[Any, Any]:
    if state.dense_index is None or state.ast_index is None:
        from codegen_rag.rag.corpus_indexing import load_indexes

        settings = get_settings(state)
        state.dense_index, state.ast_index = load_indexes(settings.path_for("faiss_index"))
    return state.dense_index, state.ast_index


def get_llm_client(state: AppState) -> Any:
    if state.llm_client is None:
        from codegen_rag.models.model_registry import UpperBoundLLMClient

        settings = get_settings(state)
        state.llm_client = UpperBoundLLMClient(
            primary=settings.upper_bound_llm.primary,
            fallback_order=settings.upper_bound_llm.fallback_order,
            max_tokens=settings.upper_bound_llm.max_tokens,
            temperature=settings.upper_bound_llm.temperature,
        )
    return state.llm_client


def get_schema_for_db(db_id: str, state: AppState) -> Any:
    if db_id in state.schema_cache:
        return state.schema_cache[db_id]

    from codegen_rag.sql.schema import introspect_sqlite_schema
    from codegen_rag.sql.spider_birdbench import find_db_path

    settings = get_settings(state)
    for dataset_key in ("spider", "birdbench"):
        databases_dir = settings.resolve_path(settings.data[dataset_key]["databases_dir"])
        db_path = find_db_path(databases_dir, db_id)
        if db_path is not None:
            schema = introspect_sqlite_schema(db_path, db_id=db_id)
            state.schema_cache[db_id] = schema
            return schema

    raise HTTPException(status_code=404, detail=f"No database found for db_id='{db_id}'")
