"""
RepoCoder Studio — Inference API

FastAPI replacement for the notebook's interactive Gradio demo (Combined Stage,
Cell 27 -- the notebook's Gradio cell also gained a RAG on/off toggle and lives
after the Stage 4/5 cells; this API mirrors that same baseline/fine-tuned +
RAG surface). Serves the baseline (pretrained) and fine-tuned (LoRA) student model for
the six supervised tasks defined in src.registry.TaskRegistry.

Corpus building, validation, and training are intentionally out of scope here —
those remain offline notebook/CLI steps. This app only loads already-trained
artifacts and serves generation requests.
"""

from __future__ import annotations

import copy
import hmac
import tempfile
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.staticfiles import StaticFiles

from app.schemas import (
    CompareRequest,
    CompareResponse,
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
    ReindexRequest,
    ReindexResponse,
    RetrievedSource,
    RepositoryInfo,
    ShowcaseInfo,
    TaskInfo,
)
from src.artifact_manifest import promote_directory
from src.config import CONFIG
from src.generation_engine import GenerationEngine
from src.generation_validation import GenerationOutputValidator
from src.demo_showcases import showcase_examples
from src.logger import LOG
from src.registry import TaskRegistry
from src.retrieval_engine import RetrievalEngine
from src.repository_catalog import (
    auto_download_enabled,
    prepare_public_repository,
    repository_catalog,
    repository_index_dirs,
    repository_path,
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
        if CONFIG.retrieval.operational_profile == "production":
            raise RuntimeError(
                "Production startup requires the configured fine-tuned adapter; "
                f"refusing baseline-only deployment: {exc}"
            ) from exc

    app.state.engine = engine
    app.state.task_registry = TaskRegistry()
    app.state.models = {
        "baseline": (baseline_model, baseline_tokenizer),
        "finetuned": (finetuned_model, finetuned_tokenizer) if finetuned_model else None,
    }
    app.state.finetuned_error = finetuned_error
    app.state.output_validator = GenerationOutputValidator(CONFIG)
    app.state.locks = {
        "baseline": threading.Lock(),
        "finetuned": threading.Lock(),
    }
    app.state.reindex_lock = threading.Lock()
    app.state.generation_semaphore = threading.BoundedSemaphore(
        CONFIG.serving.max_concurrent_generations
    )

    # Stage 4/5 — repository-aware retrieval. Loaded the same way as the
    # fine-tuned adapter: best-effort, offline artifacts only, never
    # rebuilt at request time. A missing or broken index takes the server
    # down to non-RAG generation only, not down entirely.
    retrieval_engines = {}
    repository_status = {
        row["repository_id"]: {
            **row,
            "loaded": row["repository_id"] == "generic",
            "error": None,
        }
        for row in repository_catalog()
    }
    retrieval_error = None
    if CONFIG.retrieval.enable_retrieval:
        from src.repo_explorer import RepositoryExplorer

        shared_embedder = None
        corpus_index = None
        if auto_download_enabled():
            try:
                prepare_public_repository("aws_s3", config=CONFIG)
            except Exception as exc:
                repository_status["aws_s3"]["error"] = f"download failed: {exc}"
                LOG.warning(f"AWS public demo repository unavailable: {exc}")

        for repository_id in ("ledgerflow", "aws_s3"):
            try:
                repo = repository_path(repository_id, config=CONFIG)
                if repo is None or not repo.is_dir():
                    raise FileNotFoundError(f"Repository checkout not found: {repo}")
                parsed_dir, embedding_dir = repository_index_dirs(repository_id, config=CONFIG)
                LOG.info(f"Loading Stage 4 repository index: {repository_id}")
                explorer = RepositoryExplorer(
                    repo_path=str(repo),
                    output_dir=str(parsed_dir),
                    embedding_dir=str(embedding_dir),
                    model_name=CONFIG.retrieval.embedding_model,
                    rebuild=False,
                    config=CONFIG,
                    embedder=shared_embedder,
                )
                if explorer.embedder.is_mock and not CONFIG.retrieval.allow_mock_embeddings:
                    raise RuntimeError("Real semantic embedding model is unavailable.")
                shared_embedder = explorer.embedder

                if corpus_index is None:
                    try:
                        from src.corpus_retriever import CorpusIndex

                        corpus_index = CorpusIndex(config=CONFIG, embedder=shared_embedder)
                        corpus_index.build(rebuild=False)
                    except Exception as exc:
                        corpus_index = None
                        LOG.warning(f"Corpus retrieval unavailable: {exc}")

                retrieval_engines[repository_id] = RetrievalEngine(
                    explorer, CONFIG, corpus_index=corpus_index
                )
                repository_status[repository_id]["loaded"] = True
                repository_status[repository_id]["error"] = None
            except Exception as exc:
                repository_status[repository_id]["error"] = str(exc)
                LOG.warning(f"RAG unavailable for {repository_id}: {exc}")

        if not retrieval_engines:
            retrieval_error = "No repository index could be loaded."
    else:
        retrieval_error = "Retrieval disabled via REPOCODER_ENABLE_RAG=false"

    app.state.retrieval_engines = retrieval_engines
    # Backwards-compatible alias used only by the existing admin reindex path.
    app.state.retrieval_engine = retrieval_engines.get("ledgerflow")
    app.state.repository_status = repository_status
    app.state.retrieval_error = retrieval_error

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


def _run_rag(
    task_id: str, input_text: str, use_rag: bool, repository_id: str
) -> tuple[str, bool, str, float | None, list]:
    """Returns (context, rag_used, rag_decision, rag_top_score, retrieved_sources)
    from exactly one retrieval call per request.

    RetrievalEngine.resolve() returns its full outcome directly instead of
    stashing it in shared instance state for a later call to read back --
    that matters here specifically because FastAPI can run concurrent sync
    requests, and the previous two-call version (build_context_block() then,
    after generation, a separate read of retrieval_engine.last_decision)
    left a window where a second concurrent request's retrieval could
    overwrite the first request's decision before it read it back. With one
    call and a local return value, that window doesn't exist.
    """
    if not use_rag:
        return "", False, "not_requested", None, []
    if repository_id == "generic":
        return "", False, "generic_mode_has_no_repository_rag", None, []
    retrieval_engine: RetrievalEngine | None = app.state.retrieval_engines.get(repository_id)
    if retrieval_engine is None:
        return "", False, "retrieval_unavailable", None, []
    if not retrieval_engine.is_eligible(task_id):
        return "", False, "task_not_eligible", None, []
    if not (input_text or "").strip():
        return "", False, "empty_query", None, []
    # repository_id is explicit for this endpoint. Use only the best symbol
    # from that repository; generic validated-corpus RAG remains a separate
    # evaluation/source mode and can distract a 0.5B model in repo tasks.
    outcome = retrieval_engine.resolve(
        input_text or "",
        task_id=task_id,
        top_k=1,
        sources=("repo",),
    )
    return outcome.context, outcome.used, outcome.decision.reason, outcome.decision.top_score, outcome.sources


def _run_generation(
    model_type: str, task_id: str, input_text: str, retrieved_context: str = ""
) -> str:
    entry = app.state.models.get(model_type)
    if entry is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model '{model_type}' is not loaded on this server.",
        )
    model, tokenizer = entry
    engine: GenerationEngine = app.state.engine
    instruction = engine.prompt_builder.build_instruction(task_id)
    if len(input_text or "") > CONFIG.serving.max_input_chars:
        raise HTTPException(status_code=413, detail="Input exceeds the configured size limit.")
    if not app.state.generation_semaphore.acquire(blocking=False):
        raise HTTPException(status_code=429, detail="Generation capacity is busy; retry later.")
    try:
        with app.state.locks[model_type]:
            return engine.generate(
                model,
                tokenizer,
                instruction,
                input_text or "",
                task_id=task_id,
                retrieved_context=retrieved_context,
            )
    finally:
        app.state.generation_semaphore.release()


def _retry_requirement(task_id: str) -> str:
    """Small task-specific correction used only by interactive serving."""

    if task_id in {"T1", "T4"}:
        return (
            "\n\nCorrection requirement: Return syntactically valid multi-line "
            "Python code only. Put imports and each def or class statement on "
            "separate lines. Never place def or class after a semicolon."
        )
    if task_id in {"T2", "T3"}:
        return (
            "\n\nCorrection requirement: Return one complete compilable Java "
            "class only, with balanced braces and no Markdown fences."
        )
    return (
        "\n\nCorrection requirement: Return a clear, non-empty natural-language "
        "explanation only, without code fences or response headers."
    )


def _run_validated_generation(
    model_type: str,
    task_id: str,
    input_text: str,
    retrieved_context: str,
    retry_invalid: bool,
) -> tuple[str, dict, bool, str | None, dict | None]:
    """Generate once and optionally retry, preserving the first attempt.

    Quantitative evaluation does not call this helper. The retry is a visible
    serving reliability feature and is never silently counted as first-pass
    model performance.
    """

    first_output = _run_generation(model_type, task_id, input_text, retrieved_context)
    first_validation = app.state.output_validator.validate(task_id, first_output)
    if not retry_invalid or first_validation.get("valid"):
        return first_output, first_validation, False, None, None

    retry_output = _run_generation(
        model_type,
        task_id,
        (input_text or "") + _retry_requirement(task_id),
        retrieved_context,
    )
    retry_validation = app.state.output_validator.validate(task_id, retry_output)
    if retry_validation.get("valid"):
        return retry_output, retry_validation, True, first_output, first_validation

    # Match the notebook UI: a failed correction does not replace the first
    # completion. Only a structurally valid retry is labelled and promoted.
    return first_output, first_validation, False, None, None


def _authorize_api(x_api_key: str | None) -> None:
    expected = CONFIG.serving.api_key
    if expected and (not x_api_key or not hmac.compare_digest(x_api_key, expected)):
        raise HTTPException(status_code=401, detail="Missing or invalid X-API-Key header.")


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    retrieval_engine: RetrievalEngine | None = app.state.retrieval_engines.get("ledgerflow")
    return HealthResponse(
        status="ok",
        device=_device_label(),
        baseline_loaded=app.state.models.get("baseline") is not None,
        finetuned_loaded=app.state.models.get("finetuned") is not None,
        finetuned_error=app.state.finetuned_error,
        rag_loaded=bool(app.state.retrieval_engines),
        rag_error=app.state.retrieval_error,
        rag_mock_embeddings=(
            retrieval_engine.explorer.embedder.is_mock if retrieval_engine else None
        ),
        # CorpusIndex now fails closed on mock embeddings inside build() itself
        # (src/corpus_retriever.py), so "corpus_index is None" already means
        # "unavailable, including because it would have been mock" -- this
        # field is what actually distinguishes repo-only RAG from full
        # repo+corpus RAG, which rag_mock_embeddings alone cannot (it only
        # ever reflects the repo explorer's embedder).
        rag_corpus_loaded=bool(retrieval_engine and retrieval_engine.corpus_index is not None),
        rag_repo_path=(retrieval_engine.explorer.repo_path if retrieval_engine else None),
        operational_profile=CONFIG.retrieval.operational_profile,
        index_manifest_valid=(retrieval_engine is not None),
        student_model=CONFIG.models.student_model_name,
        adapter_name=CONFIG.training.final_adapter_name,
        prompt_version=CONFIG.experiment.prompt_version,
        repositories=app.state.repository_status,
    )


@app.get("/api/tasks", response_model=list[TaskInfo])
def list_tasks() -> list[TaskInfo]:
    registry: TaskRegistry = app.state.task_registry
    return [
        TaskInfo(task_id=task_id, **info)
        for task_id, info in registry.all_tasks().items()
    ]


@app.get("/api/showcases", response_model=list[ShowcaseInfo])
def list_showcases() -> list[ShowcaseInfo]:
    """Curated prompts shared with the notebook's Gradio demo."""

    return [
        ShowcaseInfo(**row)
        for row in showcase_examples(CONFIG.storage.drive_project_root)
    ]


@app.get("/api/repositories", response_model=list[RepositoryInfo])
def list_repositories() -> list[RepositoryInfo]:
    """Repositories selectable in both the notebook and deployable UI."""

    return [
        RepositoryInfo(**app.state.repository_status[row["repository_id"]])
        for row in repository_catalog()
    ]


@app.post("/api/generate", response_model=GenerateResponse)
def generate(
    request: GenerateRequest,
    x_api_key: str | None = Header(default=None),
) -> GenerateResponse:
    _authorize_api(x_api_key)
    registry: TaskRegistry = app.state.task_registry
    if request.task_id not in registry.all_tasks():
        raise HTTPException(status_code=404, detail=f"Unknown task_id: {request.task_id}")

    context, rag_used, rag_decision, rag_top_score, sources = _run_rag(
        request.task_id, request.input_text, request.use_rag, request.repository_id
    )
    output, validation, retried, first_output, first_validation = (
        _run_validated_generation(
            request.model_type,
            request.task_id,
            request.input_text,
            context,
            request.retry_invalid,
        )
    )
    return GenerateResponse(
        task_id=request.task_id,
        model_type=request.model_type,
        repository_id=request.repository_id,
        output=output,
        rag_used=rag_used,
        rag_decision=rag_decision,
        rag_top_score=rag_top_score,
        retrieved_sources=[RetrievedSource(**s) for s in sources],
        validation=validation,
        retried=retried,
        first_output=first_output,
        first_validation=first_validation,
    )


@app.post("/api/compare", response_model=CompareResponse)
def compare(
    request: CompareRequest,
    x_api_key: str | None = Header(default=None),
) -> CompareResponse:
    _authorize_api(x_api_key)
    registry: TaskRegistry = app.state.task_registry
    if request.task_id not in registry.all_tasks():
        raise HTTPException(status_code=404, detail=f"Unknown task_id: {request.task_id}")

    # Retrieve once, reuse the same context for both models so the
    # baseline-vs-finetuned comparison isn't confounded by different context.
    context, rag_used, rag_decision, rag_top_score, sources = _run_rag(
        request.task_id, request.input_text, request.use_rag, request.repository_id
    )

    (
        baseline_output,
        baseline_validation,
        baseline_retried,
        baseline_first_output,
        baseline_first_validation,
    ) = _run_validated_generation(
        "baseline",
        request.task_id,
        request.input_text,
        context,
        request.retry_invalid,
    )

    finetuned_available = app.state.models.get("finetuned") is not None
    if finetuned_available:
        (
            finetuned_output,
            finetuned_validation,
            finetuned_retried,
            finetuned_first_output,
            finetuned_first_validation,
        ) = _run_validated_generation(
            "finetuned",
            request.task_id,
            request.input_text,
            context,
            request.retry_invalid,
        )
    else:
        finetuned_output = None
        finetuned_validation = None
        finetuned_retried = False
        finetuned_first_output = None
        finetuned_first_validation = None

    return CompareResponse(
        task_id=request.task_id,
        repository_id=request.repository_id,
        baseline_output=baseline_output,
        finetuned_output=finetuned_output,
        finetuned_available=finetuned_available,
        rag_used=rag_used,
        rag_decision=rag_decision,
        rag_top_score=rag_top_score,
        retrieved_sources=[RetrievedSource(**s) for s in sources],
        baseline_validation=baseline_validation,
        finetuned_validation=finetuned_validation,
        baseline_retried=baseline_retried,
        finetuned_retried=finetuned_retried,
        baseline_first_output=baseline_first_output,
        finetuned_first_output=finetuned_first_output,
        baseline_first_validation=baseline_first_validation,
        finetuned_first_validation=finetuned_first_validation,
    )


@app.post("/api/admin/reindex", response_model=ReindexResponse)
def admin_reindex(request: ReindexRequest, x_admin_token: str | None = Header(default=None)) -> ReindexResponse:
    """Re-points Stage 4 (and optionally Stage 5's corpus index) at a
    different repository without redeploying the container -- the "real
    world use, point at your own repo" capability.

    Deliberately narrow for safety: repo_path must already exist on this
    server's mounted volume. This endpoint never clones, fetches, or
    otherwise reaches out to anything remote -- get the repo onto the
    volume first (docker cp, a different volume mount, a shell into the
    container, etc.), then call this. That's what keeps this from being
    an SSRF-style surface: a client can never make this server issue an
    outbound request to an address of their choosing.

    Gated by REPOCODER_ADMIN_TOKEN (X-Admin-Token header). Unset by
    default -- a deployment doesn't get this surface just because the
    code supports it; it has to be turned on on purpose.
    """
    admin_token = CONFIG.retrieval.admin_reindex_token
    if not CONFIG.retrieval.enable_online_reindex:
        raise HTTPException(
            status_code=503,
            detail="Online reindex is disabled. Use the offline index build job.",
        )
    if not admin_token:
        raise HTTPException(
            status_code=503,
            detail="Admin reindex is disabled. Set REPOCODER_ADMIN_TOKEN to enable it.",
        )
    if not x_admin_token or not hmac.compare_digest(x_admin_token, admin_token):
        raise HTTPException(status_code=401, detail="Missing or invalid X-Admin-Token header.")

    repo_path = Path(request.repo_path).resolve()
    allowed_root = Path(CONFIG.retrieval.allowed_repo_root).resolve()
    if repo_path != allowed_root and allowed_root not in repo_path.parents:
        raise HTTPException(
            status_code=403,
            detail=f"Repository path must be inside the configured repository root: {allowed_root}",
        )
    if not repo_path.is_dir():
        raise HTTPException(
            status_code=404,
            detail=(
                f"Repo path not found on this server: {repo_path}. This endpoint never "
                "clones or fetches anything remote -- get the repo onto the server's "
                "mounted volume first, then retry."
            ),
        )

    from src.repo_explorer import RepositoryExplorer
    if not app.state.reindex_lock.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="A repository index build is already running.")

    try:
        with tempfile.TemporaryDirectory(prefix="repocoder_reindex_") as tmp:
            staged_root = Path(tmp)
            staged_output = staged_root / "output"
            staged_embeddings = staged_root / "embeddings"
            explorer = RepositoryExplorer(
                repo_path=str(repo_path),
                output_dir=str(staged_output),
                embedding_dir=str(staged_embeddings),
                model_name=CONFIG.retrieval.embedding_model,
                rebuild=True,
                config=CONFIG,
            )
            if explorer.embedder.is_mock and not CONFIG.retrieval.allow_mock_embeddings:
                raise RuntimeError("Real embedding model unavailable; index was not promoted.")
            report = explorer.generate_summary_report()
            promote_directory(staged_output, app.state.engine.config.storage.project_root() / CONFIG.storage.repo_explorer_output_dir)
            promote_directory(
                staged_embeddings,
                app.state.engine.config.storage.project_root() / CONFIG.storage.repo_explorer_embedding_dir,
            )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Reindex failed: {exc}") from exc
    finally:
        app.state.reindex_lock.release()

    try:
        migration_status = explorer.migration_status()
    except Exception as exc:
        LOG.warning(f"Admin reindex: migration_status() not applicable for this repo: {exc}")
        migration_status = None

    previous_engine: RetrievalEngine | None = app.state.retrieval_engine
    corpus_index = previous_engine.corpus_index if previous_engine else None
    corpus_rows_indexed = None
    if request.rebuild_corpus:
        try:
            from src.corpus_retriever import CorpusIndex

            # Reuses the just-rebuilt explorer's embedder rather than
            # loading a second, separate copy of the same model.
            corpus_index = CorpusIndex(config=CONFIG, embedder=explorer.embedder)
            corpus_rows_indexed = corpus_index.build(rebuild=True)
        except Exception as exc:
            LOG.warning(f"Admin reindex: corpus rebuild failed, keeping previous corpus index: {exc}")
    elif corpus_index is not None:
        # Keep the CorpusIndex used by in-flight requests untouched. A
        # shallow copy safely shares its read-only FAISS indices/metadata,
        # while query embedding is rebound to the new explorer's already
        # loaded model. Repo-only reindex therefore still keeps one embedding
        # model resident in the replacement retrieval engine.
        corpus_index = copy.copy(corpus_index)
        corpus_index.embedder = explorer.embedder

    # Build the new engine fully before touching app.state -- readers of
    # app.state.retrieval_engine mid-request see either the complete old
    # engine or the complete new one, never a partially-rebuilt one.
    replacement_engine = RetrievalEngine(explorer, CONFIG, corpus_index=corpus_index)
    app.state.retrieval_engine = replacement_engine
    app.state.retrieval_engines["ledgerflow"] = replacement_engine
    app.state.repository_status["ledgerflow"]["loaded"] = True
    app.state.repository_status["ledgerflow"]["error"] = None
    app.state.retrieval_error = None

    LOG.info(f"Admin reindex complete: {repo_path} ({report['total_files']} files)")

    return ReindexResponse(
        status="ok",
        repo_path=str(repo_path),
        files=report["total_files"],
        functions=report["total_functions"],
        classes=report["total_classes"],
        mock_embeddings=report["mock_embeddings"],
        migration_status=migration_status,
        corpus_rows_indexed=corpus_rows_indexed,
    )


app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
