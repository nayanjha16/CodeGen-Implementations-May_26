"""Cold-session loader for the RepoCoderStudio Gradio showcase.

This module restores serving artifacts only.  It never trains a model,
evaluates a dataset, downloads a public repository, or rebuilds a FAISS
index.  Missing/stale artifacts therefore fail with an actionable message
instead of starting an unexpected expensive job.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import inspect
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence


@dataclass
class GradioRuntime:
    """Objects needed by ``build_gradio_showcase``."""

    config: Any
    generation_engine: Any
    baseline_model: Any
    baseline_tokenizer: Any
    finetuned_model: Any
    finetuned_tokenizer: Any
    retrieval_engines: dict[str, Any]
    task_registry: Any
    output_validator: Any
    corpus_rows: int
    reused_models: bool

    def ui_arguments(self) -> dict[str, Any]:
        """Return keyword arguments accepted by ``build_gradio_showcase``."""

        return {
            "gen_engine": self.generation_engine,
            "baseline_model": self.baseline_model,
            "baseline_tokenizer": self.baseline_tokenizer,
            "finetuned_model": self.finetuned_model,
            "finetuned_tokenizer": self.finetuned_tokenizer,
            "retrieval_engines": self.retrieval_engines,
            "task_registry": self.task_registry,
            "output_validator": self.output_validator,
            "project_root": self.config.storage.project_root(),
        }


def _missing(paths: Sequence[Path]) -> list[Path]:
    return [path for path in paths if not path.is_file()]


def _require_files(label: str, paths: Sequence[Path]) -> None:
    missing = _missing(paths)
    if missing:
        rendered = "\n".join(f"  - {path}" for path in missing)
        raise FileNotFoundError(
            f"{label} is incomplete. Missing:\n{rendered}\n"
            "Run the corresponding save/index cell once; this Gradio-only "
            "loader deliberately will not rebuild artifacts."
        )


def _config_for_root(project_root: str | Path | None):
    from src.config import CONFIG

    if project_root is None:
        return CONFIG
    root = Path(project_root).expanduser().resolve()
    return replace(
        CONFIG,
        storage=replace(CONFIG.storage, drive_project_root=str(root)),
    )


def _require_adapter(config) -> None:
    adapter_dir = (
        config.storage.project_root()
        / config.storage.adapters_dir
        / config.training.final_adapter_name
    )
    weights = [
        adapter_dir / "adapter_model.safetensors",
        adapter_dir / "adapter_model.bin",
    ]
    _require_files("Fine-tuned LoRA adapter", [adapter_dir / "adapter_config.json"])
    if not any(path.is_file() for path in weights):
        raise FileNotFoundError(
            "Fine-tuned LoRA adapter weights are missing. Expected one of:\n"
            + "\n".join(f"  - {path}" for path in weights)
        )


def _require_repository_artifacts(config, repository_id: str) -> None:
    from src.repository_catalog import repository_index_dirs, repository_path

    repo = repository_path(repository_id, config=config)
    if repo is None or not repo.is_dir():
        raise FileNotFoundError(
            f"Repository source folder is missing for {repository_id}: {repo}\n"
            "Keep the bundled/downloaded repository beside outputs; the loader "
            "uses it to validate the cached index manifest."
        )
    _parsed_dir, embedding_dir = repository_index_dirs(repository_id, config=config)
    required = [embedding_dir / "index_manifest.json"]
    for kind in ("function", "class", "module"):
        required.extend(
            [
                embedding_dir / f"{kind}_embeddings.npy",
                embedding_dir / f"{kind}_metadata.json",
                embedding_dir / f"{kind}_index.faiss",
            ]
        )
    _require_files(f"Stage 4 index for {repository_id}", required)


def _require_corpus_artifacts(config) -> None:
    root = config.storage.project_root()
    index_dir = root / config.storage.corpus_index_dir
    approved = root / config.storage.approved_corpus_dir / "approved_corpus.jsonl"
    _require_files(
        "Stage 5 approved-corpus index",
        [
            approved,
            index_dir / "corpus_index_manifest.json",
            index_dir / "corpus_index_metadata.json",
            index_dir / "corpus_index.faiss",
            index_dir / "corpus_nl_index.faiss",
            index_dir / "corpus_java_index.faiss",
        ],
    )


def patch_gradio_template_compatibility() -> bool:
    """Bridge Gradio 4.44's old TemplateResponse call to new Starlette.

    Returns ``True`` only when the compatibility wrapper was newly applied.
    It is safe to call this every time the launch cell is run.
    """

    from starlette.templating import Jinja2Templates

    current = Jinja2Templates.TemplateResponse
    if getattr(current, "_repocoder_gradio_compat", False):
        return False

    parameters = list(inspect.signature(current).parameters)
    # Old Starlette is already compatible with Gradio 4.44: (self, name,
    # context, ...).  New Starlette is request-first: (self, request, name,...).
    effective = [name for name in parameters if name != "self"]
    if not effective or effective[0] != "request":
        return False

    original = current

    def compatible(self, *args, **kwargs):
        old_style = bool(args and isinstance(args[0], str))
        old_style = old_style or (
            not args and "name" in kwargs and "request" not in kwargs
        )
        if not old_style:
            return original(self, *args, **kwargs)

        values = dict(kwargs)
        name = args[0] if args else values.pop("name")
        context = args[1] if len(args) > 1 else values.pop("context", None)
        context = dict(context or {})
        request = context.get("request")
        if request is None:
            raise RuntimeError(
                "Gradio supplied an old-style TemplateResponse without "
                "context['request']; cannot apply the Starlette compatibility shim."
            )

        positional_names = ("status_code", "headers", "media_type", "background")
        for key, value in zip(positional_names, args[2:]):
            values.setdefault(key, value)
        return original(
            self,
            request=request,
            name=name,
            context=context,
            **values,
        )

    compatible._repocoder_gradio_compat = True
    compatible.__name__ = getattr(original, "__name__", "TemplateResponse")
    compatible.__doc__ = getattr(original, "__doc__", None)
    Jinja2Templates.TemplateResponse = compatible
    return True


def load_gradio_runtime(
    project_root: str | Path | None = None,
    *,
    reuse: Optional[Mapping[str, Any]] = None,
    repository_ids: Sequence[str] = ("ledgerflow", "aws_s3"),
) -> GradioRuntime:
    """Restore models and retrieval indexes for a Gradio-only session.

    ``reuse`` is optional.  The launch cell uses it when the full notebook has
    already loaded models/indexes, preventing duplicate GPU allocations.  In a
    fresh session the mapping is empty and every serving object is restored.
    """

    from src.corpus_retriever import CorpusIndex
    from src.generation_engine import GenerationEngine
    from src.generation_validation import GenerationOutputValidator
    from src.registry import TaskRegistry
    from src.repo_explorer import RepositoryExplorer
    from src.repository_catalog import repository_index_dirs, repository_path
    from src.retrieval_engine import RetrievalEngine

    config = _config_for_root(project_root)
    root = config.storage.project_root()
    if not root.is_dir():
        raise FileNotFoundError(f"RepoCoderStudio project folder not found: {root}")

    reuse = dict(reuse or {})
    engine = reuse.get("generation_engine") or GenerationEngine(config)

    baseline_model = reuse.get("baseline_model")
    baseline_tokenizer = reuse.get("baseline_tokenizer")
    finetuned_model = reuse.get("finetuned_model")
    finetuned_tokenizer = reuse.get("finetuned_tokenizer")
    models_reused = all(
        value is not None
        for value in (
            baseline_model,
            baseline_tokenizer,
            finetuned_model,
            finetuned_tokenizer,
        )
    )

    if baseline_model is None or baseline_tokenizer is None:
        print("Loading pretrained baseline model...")
        baseline_model, baseline_tokenizer = engine.load_model("baseline")
    if finetuned_model is None or finetuned_tokenizer is None:
        _require_adapter(config)
        print("Loading saved fine-tuned LoRA adapter from outputs...")
        finetuned_model, finetuned_tokenizer = engine.load_model("finetuned")
    if models_reused:
        print("Reusing baseline and fine-tuned models already in memory.")

    retrieval_engines = dict(reuse.get("retrieval_engines") or {})
    shared_embedder = None
    if retrieval_engines:
        shared_embedder = next(iter(retrieval_engines.values())).explorer.embedder

    # Load the corpus once, sharing the same immutable embedding model used by
    # every repository explorer.  Preflight prevents build(False) from falling
    # through into a rebuild when a cache file is absent.
    _require_corpus_artifacts(config)
    corpus_index = None
    if retrieval_engines:
        corpus_index = next(iter(retrieval_engines.values())).corpus_index

    for repository_id in repository_ids:
        if repository_id in retrieval_engines:
            continue
        _require_repository_artifacts(config, repository_id)
        repo = repository_path(repository_id, config=config)
        parsed_dir, embedding_dir = repository_index_dirs(repository_id, config=config)
        print(f"Loading saved Stage 4 index: {repository_id}")
        explorer = RepositoryExplorer(
            repo_path=str(repo),
            output_dir=str(parsed_dir),
            embedding_dir=str(embedding_dir),
            model_name=config.retrieval.embedding_model,
            rebuild=False,
            config=config,
            embedder=shared_embedder,
        )
        if explorer.embedder.is_mock and not config.retrieval.allow_mock_embeddings:
            raise RuntimeError(
                f"{repository_id} loaded mock embeddings; refusing to serve misleading RAG."
            )
        shared_embedder = explorer.embedder
        if corpus_index is None:
            print("Loading saved Stage 5 corpus indexes...")
            corpus_index = CorpusIndex(config=config, embedder=shared_embedder)
            corpus_rows = corpus_index.build(rebuild=False)
            if corpus_rows <= 0:
                raise RuntimeError("The saved Stage 5 corpus index contains no rows.")
        retrieval_engines[repository_id] = RetrievalEngine(
            explorer,
            config,
            corpus_index=corpus_index,
        )

    if not retrieval_engines:
        raise RuntimeError("No Stage 4 repository retrieval engine could be restored.")
    if corpus_index is None:
        raise RuntimeError("The Stage 5 corpus retrieval index could not be restored.")

    corpus_rows = len(getattr(corpus_index, "_rows", []))
    runtime = GradioRuntime(
        config=config,
        generation_engine=engine,
        baseline_model=baseline_model,
        baseline_tokenizer=baseline_tokenizer,
        finetuned_model=finetuned_model,
        finetuned_tokenizer=finetuned_tokenizer,
        retrieval_engines=retrieval_engines,
        task_registry=reuse.get("task_registry") or TaskRegistry(),
        output_validator=(
            reuse.get("output_validator") or GenerationOutputValidator(config)
        ),
        corpus_rows=corpus_rows,
        reused_models=models_reused,
    )
    print("\nGradio serving runtime ready")
    print(f"  Project root     : {root}")
    print(f"  Fine-tuned model : loaded")
    print(f"  RAG repositories : {', '.join(sorted(retrieval_engines))}")
    print(f"  Corpus rows      : {corpus_rows}")
    return runtime
