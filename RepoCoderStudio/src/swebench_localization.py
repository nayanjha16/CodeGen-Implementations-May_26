"""
============================================================
RepoCoder Studio
swebench_localization.py — small, honest SWE-bench Lite proof-of-concept
============================================================

Answers a narrower, Stage-4-appropriate question with real SWE-bench
Lite data: given a real GitHub issue's text, does Stage 4's retrieval,
searching the *actual* repository at the *actual* pre-fix commit,
surface the file(s) the *actual* accepted patch touched, in the top-k?
That's a genuine file-localization signal — directly the proposal's
"File/Function Identification Accuracy" metric for Stage 4 — using real
issues and real accepted patches, not invented data.

Scope and honesty (read this before trusting a number from this module)
-------------------------------------------------------------------------
This is explicitly NOT a full SWE-bench evaluation. The real SWE-bench
protocol additionally requires generating a patch and running each
instance's FAIL_TO_PASS/PASS_TO_PASS tests inside a per-instance-pinned
environment (SWE-bench's own harness uses one Docker image per
instance for exactly this reason) — that's an end-to-end agentic
bug-fixing evaluation, not a retrieval-quality one, and belongs to
Stage 6's Planner/Retriever/Generator/Validator loop, not Stage 4. This
module stops at "did retrieval find the right file," deliberately.

Cost note: each instance requires a partial git clone (--filter=blob:none,
avoids downloading full history) of a real open-source repository plus a
full Stage 4 index build. Even lightweight repos (requests, flask) take
several seconds each; larger ones (django, astropy, matplotlib) take
longer and use more disk. Keep num_instances small (the notebook cell
defaults to 3) — this is a proof-of-concept, not a benchmark run at scale.
Each instance's clone is deleted after indexing, not left on disk.
"""

from __future__ import annotations

import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from src.config import AppConfig, CONFIG
from src.logger import LOG
from src.storage import ProjectStorageManager
from src.repo_clone_utils import clone_at_commit

SWEBENCH_DATASET = "princeton-nlp/SWE-bench_Lite"
SWEBENCH_SPLIT = "test"
_FILE_HEADER_RE = re.compile(r"^diff --git a/(\S+) b/\S+", re.MULTILINE)


def _changed_files(patch_text: str) -> List[str]:
    """Extracts the list of file paths touched by a unified diff's
    'diff --git a/<path> b/<path>' headers."""
    return _FILE_HEADER_RE.findall(patch_text or "")


def evaluate_swebench_localization(
    num_instances: int = 3,
    top_k: int = 10,
    split: str = SWEBENCH_SPLIT,
    config: AppConfig = CONFIG,
) -> Dict[str, Any]:
    """Runs the file-localization proof-of-concept against real SWE-bench
    Lite instances. Returns {"status": "skipped", "reason": ...} if the
    `datasets` library isn't available -- optional and best-effort, same
    as evaluate_repobench(), never blocks the rest of Stage 4/5."""
    try:
        from datasets import load_dataset
    except ImportError as exc:
        LOG.warning(f"SWE-bench localization skipped: 'datasets' library not installed ({exc})")
        return {"status": "skipped", "reason": "datasets library not installed"}

    from src.repo_explorer import RepositoryExplorer

    LOG.info(f"Streaming up to {num_instances} instances from {SWEBENCH_DATASET} ({split}) ...")
    try:
        ds = load_dataset(SWEBENCH_DATASET, split=split, streaming=True)
    except Exception as exc:
        LOG.warning(f"SWE-bench localization skipped: could not load dataset ({exc})")
        return {"status": "skipped", "reason": repr(exc)}

    instances = []
    try:
        for row in ds:
            if len(instances) >= num_instances:
                break
            if _changed_files(row.get("patch", "")):
                instances.append(row)
    except Exception as exc:
        LOG.warning(f"SWE-bench localization skipped: error while streaming instances ({exc})")
        return {"status": "skipped", "reason": repr(exc)}

    if not instances:
        return {"status": "skipped", "reason": "no usable instances retrieved"}

    per_instance: List[Dict[str, Any]] = []
    hits = 0
    mock_embeddings = None

    for row in instances:
        instance_id = row["instance_id"]
        repo = row["repo"]
        base_commit = row["base_commit"]
        gold_files = set(_changed_files(row["patch"]))

        with tempfile.TemporaryDirectory(prefix="swebench_") as tmp:
            repo_dir = Path(tmp) / "repo"
            cloned = clone_at_commit(repo, base_commit, repo_dir)
            if not cloned:
                per_instance.append({"instance_id": instance_id, "status": "clone_failed"})
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
                results = explorer.search(row["problem_statement"], top_k=top_k)
            except Exception as exc:
                LOG.warning(f"SWE-bench localization: indexing/search failed for {instance_id}: {exc}")
                per_instance.append({"instance_id": instance_id, "status": "index_failed", "error": repr(exc)})
                continue

            retrieved_files = {r.file_path for r in results}
            hit = bool(gold_files & retrieved_files)
            if hit:
                hits += 1
            per_instance.append({
                "instance_id": instance_id,
                "repo": repo,
                "status": "ok",
                "gold_files": sorted(gold_files),
                "retrieved_files_top_k": sorted(retrieved_files),
                "hit": hit,
            })
            # shutil not strictly needed (TemporaryDirectory self-cleans),
            # but explicit for clarity that nothing is left on disk.
            shutil.rmtree(repo_dir, ignore_errors=True)

    evaluated = [r for r in per_instance if r["status"] == "ok"]
    n = len(evaluated)
    metrics: Dict[str, Any] = {
        "status": "ok" if n else "no_successful_instances",
        "dataset": SWEBENCH_DATASET,
        "split": split,
        "instances_attempted": len(instances),
        "instances_evaluated": n,
        "top_k": top_k,
        "file_localization_hit_rate": round(hits / n, 4) if n else None,
        "mock_embeddings": mock_embeddings,
        "per_instance": per_instance,
        "scope_note": (
            "File-localization only (does the issue text retrieve the right file "
            "in top-k) -- not a full SWE-bench evaluation. No patch was generated "
            "and no tests were run; see this module's docstring."
        ),
    }

    storage = ProjectStorageManager(config)
    storage.save_json(metrics, storage.swebench_localization_report_path())
    return metrics
