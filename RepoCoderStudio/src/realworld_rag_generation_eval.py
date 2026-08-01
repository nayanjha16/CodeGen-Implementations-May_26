"""
============================================================
RepoCoder Studio
realworld_rag_generation_eval.py — RAG-grounded generation quality on
real, externally-authored repositories (RepoBench-sourced)
============================================================

Closes the loop from "is Stage 4/5's retrieval mechanism any good"
(src/repobench_eval.py, per-row candidate ranking) to "does grounding
the fine-tuned model's generation in Stage 4/5 RAG measurably improve
output quality, on real repositories, not just this project's own
validated corpus" -- directly the "evaluate the model created using
Stage 4 and Stage 5" question this module exists to answer.

Task framing
------------
RepoBench rows already carry a real completion task: given `cropped_code`
(a real file with a gap) from a real repository, predict the single
`next_line`. This module:

1. Picks a small number of distinct real repositories referenced by
   sampled RepoBench rows and clones each ONCE (current default-branch
   HEAD -- RepoBench rows carry no commit pin, so exact historical
   reproduction isn't available here the way it is for SWE-bench Lite's
   file-localization check; rows whose file_path no longer exists in the
   current HEAD checkout are skipped rather than silently scored against
   a target that may no longer be accurate).
2. Indexes each cloned repository with Stage 4 (RepositoryExplorer).
3. For each row, against its own repository's index: builds a Stage 5
   RAG context with sources=("repo",) -- deliberately NOT the demo repo
   or CorpusIndex, both of which are irrelevant to a real external
   repo's own code (same reasoning src/evaluator.py already applies in
   the other direction for its own corpus-only evaluation).
4. Runs baseline and fine-tuned models, RAG-on and RAG-off (up to 4
   combinations), through the same GenerationEngine used everywhere else
   in this project, with a plain completion-style prompt (task_id="",
   which is the project's existing generic prompt path) -- "complete
   this real-world code" isn't any of the six T1-T6 task contracts, and
   forcing it through one of those would be a worse fit than the
   generic path this project's own prompt_builder.py already provides.
5. Scores each generation against the real next_line target with the
   same metric family RepoBench's own published evaluation uses: Exact
   Match and Edit Similarity (rapidfuzz.fuzz.ratio(), Levenshtein-based;
   falls back to difflib if rapidfuzz isn't installed).
6. Aggregates baseline-vs-fine-tuned and RAG-vs-no-RAG results.

This needs actual model generation (torch/transformers) and therefore
cannot be run or verified in an environment without those installed --
the same boundary every other generation-dependent piece of this
project sits behind. Cloning, indexing, RAG context construction, task
sampling, and the EM/ES scoring math are all independently verifiable
without the model and were verified that way; see the notebook cell's
comments for what was and wasn't run in this environment.
"""

from __future__ import annotations

import difflib
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.config import AppConfig, CONFIG
from src.logger import LOG
from src.storage import ProjectStorageManager
from src.repo_clone_utils import clone_at_commit
from src.evaluation_statistics import paired_bootstrap_delta

REPOBENCH_DATASETS = {
    "python": "tianyang/repobench_python_v1.1",
    "java": "tianyang/repobench_java_v1.1",
}
REPOBENCH_SPLIT = "cross_file_first"
_QUERY_CHARS = 800
_MAX_ROWS_SCANNED = 3000  # safety cap while streaming, in case a language/split lacks enough repo diversity


def _sample_tasks_by_repo(language: str, num_repos: int, rows_per_repo: int, split: str) -> Dict[str, List[dict]]:
    from datasets import load_dataset

    dataset_name = REPOBENCH_DATASETS[language]
    ds = load_dataset(dataset_name, split=split, streaming=True)

    by_repo: Dict[str, List[dict]] = {}
    scanned = 0
    for row in ds:
        scanned += 1
        if scanned > _MAX_ROWS_SCANNED:
            break
        repo = row.get("repo_name")
        if not repo or not row.get("next_line", "").strip():
            continue
        if repo not in by_repo:
            if len(by_repo) >= num_repos:
                continue
            by_repo[repo] = []
        if len(by_repo[repo]) < rows_per_repo:
            by_repo[repo].append(row)
        if len(by_repo) >= num_repos and all(len(v) >= rows_per_repo for v in by_repo.values()):
            break
    return by_repo


def _exact_match(pred: str, gold: str) -> bool:
    return pred.strip() == gold.strip()


def _edit_similarity(pred: str, gold: str) -> float:
    pred, gold = pred.strip(), gold.strip()
    try:
        from rapidfuzz import fuzz
        return fuzz.ratio(pred, gold) / 100.0
    except ImportError:
        return difflib.SequenceMatcher(None, pred, gold).ratio()


def _first_generated_line(text: str) -> str:
    """Normalize a completion response to RepoBench's single-line target."""
    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith(("```", "###")):
            return stripped
    return ""


def _snapshot_anchor_matches(repo_file: Path, cropped_code: str, anchor_chars: int = 240) -> bool:
    """Reject current-HEAD files that no longer contain the benchmark prefix."""
    try:
        current = repo_file.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    anchor = (cropped_code or "").strip()[-anchor_chars:]
    return bool(anchor) and anchor in current


def evaluate_realworld_generation(
    gen_engine,
    models: Dict[str, Optional[Tuple[Any, Any]]],
    language: str = "python",
    num_repos: int = 2,
    rows_per_repo: int = 4,
    top_k: int = 5,
    config: AppConfig = CONFIG,
) -> Dict[str, Any]:
    """models: {"baseline": (model, tokenizer), "finetuned": (model, tokenizer) or None}
    -- pass the already-loaded models from the notebook's Stage 5 cell
    rather than loading fresh ones (same reasoning as evaluator.py's
    model=/tokenizer= parameters: this project has real Colab T4 CUDA
    OOM history from redundant model loads).

    Returns {"status": "skipped", "reason": ...} if the `datasets`
    library isn't available -- optional and best-effort, same as
    evaluate_repobench() / evaluate_swebench_localization(), never
    blocks the rest of Stage 4/5 from running.
    """
    if language not in REPOBENCH_DATASETS:
        return {"status": "skipped", "reason": f"unknown language {language!r}"}

    try:
        import datasets  # noqa: F401
    except ImportError as exc:
        LOG.warning(f"Real-world generation evaluation skipped: 'datasets' library not installed ({exc})")
        return {"status": "skipped", "reason": "datasets library not installed"}

    from src.repo_explorer import RepositoryExplorer
    from src.retrieval_engine import RetrievalEngine

    active_models = {k: v for k, v in models.items() if v is not None}
    if not active_models:
        return {"status": "skipped", "reason": "no models provided"}

    LOG.info(
        f"Sampling RepoBench ({language}) rows grouped by repo: "
        f"up to {num_repos} repos x {rows_per_repo} rows ..."
    )
    try:
        by_repo = _sample_tasks_by_repo(language, num_repos, rows_per_repo, REPOBENCH_SPLIT)
    except Exception as exc:
        LOG.warning(f"Real-world generation evaluation skipped: could not sample RepoBench ({exc})")
        return {"status": "skipped", "reason": repr(exc)}

    if not by_repo:
        return {"status": "skipped", "reason": "no usable rows retrieved"}

    per_row: List[Dict[str, Any]] = []
    mock_embeddings = None

    for repo_name, rows in by_repo.items():
        with tempfile.TemporaryDirectory(prefix="realworld_rag_") as tmp:
            repo_dir = Path(tmp) / "repo"
            # RepoBench rows carry no commit pin -- clone at the repo's
            # current default-branch HEAD, the closest available
            # approximation (see module docstring).
            cloned = clone_at_commit(repo_name, "HEAD", repo_dir)
            if not cloned:
                for row in rows:
                    per_row.append({"repo": repo_name, "file_path": row["file_path"], "status": "clone_failed"})
                continue

            try:
                explorer = RepositoryExplorer(
                    repo_path=str(repo_dir),
                    output_dir=str(Path(tmp) / "index"),
                    embedding_dir=str(Path(tmp) / "embeddings"),
                    model_name=config.retrieval.embedding_model,
                    rebuild=True,
                    config=config,
                )
                mock_embeddings = explorer.embedder.is_mock
                retrieval_engine = RetrievalEngine(explorer, config)
            except Exception as exc:
                LOG.warning(f"Real-world eval: indexing failed for {repo_name}: {exc}")
                for row in rows:
                    per_row.append({"repo": repo_name, "file_path": row["file_path"], "status": "index_failed"})
                continue

            for row in rows:
                file_path = row["file_path"]
                if not (repo_dir / file_path).exists():
                    # File no longer exists at HEAD -- the row's next_line
                    # target can't be trusted as still-accurate; skip
                    # rather than silently score against a stale target.
                    per_row.append({"repo": repo_name, "file_path": file_path, "status": "file_not_in_head"})
                    continue
                if not _snapshot_anchor_matches(repo_dir / file_path, row.get("cropped_code", "")):
                    per_row.append(
                        {
                            "repo": repo_name,
                            "file_path": file_path,
                            "status": "snapshot_mismatch",
                        }
                    )
                    continue

                query = (row.get("import_statement", "") + "\n" + row["cropped_code"])[-_QUERY_CHARS:]
                gold = row["next_line"]
                instruction = "Complete the following code with a single next line."

                row_result: Dict[str, Any] = {
                    "repo": repo_name, "file_path": file_path, "status": "ok", "gold": gold,
                }
                for model_type, (model, tokenizer) in active_models.items():
                    for rag_mode, use_rag in (("no_rag", False), ("with_rag", True)):
                        context = ""
                        if use_rag:
                            context = retrieval_engine.build_context_block(query, sources=("repo",), top_k=top_k)
                        try:
                            raw_pred = gen_engine.generate(
                                model, tokenizer, instruction, query, retrieved_context=context
                            )
                            pred = _first_generated_line(raw_pred)
                        except Exception as exc:
                            LOG.warning(
                                f"Real-world eval: generation failed for {repo_name}/{file_path} "
                                f"({model_type}/{rag_mode}): {exc}"
                            )
                            pred = ""
                        key = f"{model_type}_{rag_mode}"
                        row_result[f"{key}_prediction"] = pred
                        row_result[f"{key}_exact_match"] = _exact_match(pred, gold)
                        row_result[f"{key}_edit_similarity"] = round(_edit_similarity(pred, gold), 4)
                per_row.append(row_result)

    evaluated = [r for r in per_row if r["status"] == "ok"]
    n = len(evaluated)

    def _agg(model_type: str, rag_mode: str, metric: str) -> Optional[float]:
        field = f"{model_type}_{rag_mode}_{metric}"
        vals = [r[field] for r in evaluated if field in r]
        if not vals:
            return None
        if metric == "exact_match":
            return round(sum(1 for v in vals if v) / len(vals), 4)
        return round(sum(vals) / len(vals), 4)

    summary: Dict[str, Any] = {}
    for model_type in active_models:
        for rag_mode in ("no_rag", "with_rag"):
            summary[f"{model_type}_{rag_mode}"] = {
                "exact_match": _agg(model_type, rag_mode, "exact_match"),
                "edit_similarity": _agg(model_type, rag_mode, "edit_similarity"),
            }
        summary[f"{model_type}_rag_lift"] = {
            "exact_match": paired_bootstrap_delta(
                [
                    float(r.get(f"{model_type}_no_rag_exact_match", False))
                    for r in evaluated
                ],
                [
                    float(r.get(f"{model_type}_with_rag_exact_match", False))
                    for r in evaluated
                ],
                seed=config.runtime.random_seed,
            ),
            "edit_similarity": paired_bootstrap_delta(
                [
                    float(r.get(f"{model_type}_no_rag_edit_similarity", 0.0))
                    for r in evaluated
                ],
                [
                    float(r.get(f"{model_type}_with_rag_edit_similarity", 0.0))
                    for r in evaluated
                ],
                seed=config.runtime.random_seed,
            ),
        }

    metrics: Dict[str, Any] = {
        "status": "ok" if n else "no_successful_rows",
        "language": language,
        "dataset": REPOBENCH_DATASETS[language],
        "repos_used": list(by_repo.keys()),
        "rows_attempted": len(per_row),
        "rows_evaluated": n,
        "mock_embeddings": mock_embeddings,
        "summary": summary,
        "per_row": per_row,
        "scope_note": (
            "RepoBench rows carry no commit pin, so repos are cloned at current HEAD. Rows are "
            "scored only when the benchmark prefix is still present in the current file; missing "
            "or changed snapshots are skipped. Edit similarity uses rapidfuzz.fuzz.ratio(), matching "
            "RepoBench's own published Exact Match / Edit Similarity protocol. Generation uses a "
            "plain completion prompt (task_id=\"\"), not one of the six T1-T6 task contracts."
        ),
    }

    storage = ProjectStorageManager(config)
    storage.save_json(metrics, storage.realworld_generation_eval_report_path(language=language))
    return metrics
