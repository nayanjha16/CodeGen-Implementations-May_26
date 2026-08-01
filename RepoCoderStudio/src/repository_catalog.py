"""Shared repository catalogue for the notebook, Gradio UI, and FastAPI UI."""

from __future__ import annotations

import os
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

from src.config import CONFIG, AppConfig


@dataclass(frozen=True)
class RepositorySpec:
    repository_id: str
    title: str
    description: str
    languages: List[str]
    relative_path: Optional[str]
    rag_available: bool
    public_url: Optional[str] = None
    license: Optional[str] = None


REPOSITORIES: Dict[str, RepositorySpec] = {
    "generic": RepositorySpec(
        repository_id="generic",
        title="Generic examples (RAG off)",
        description="Small language examples that do not claim repository grounding.",
        languages=["Python", "Java"],
        relative_path=None,
        rag_available=False,
    ),
    "ledgerflow": RepositorySpec(
        repository_id="ledgerflow",
        title="LedgerFlow banking sample",
        description=(
            "Bundled bilingual banking repository with Python services and selected "
            "Java migration targets, policies, fraud, KYC, transfers, and audit APIs."
        ),
        languages=["Python", "Java"],
        relative_path="repo_explorer_data/sample_repo",
        rag_available=True,
        license="Capstone sample repository",
    ),
    "aws_s3": RepositorySpec(
        repository_id="aws_s3",
        title="AWS SDK S3 examples (public)",
        description=(
            "Sparse checkout of AWS's official Python and Java v2 S3 examples; "
            "the exact downloaded commit is recorded for reproducibility."
        ),
        languages=["Python", "Java"],
        relative_path="repo_explorer_data/public_demo/aws_sdk_s3",
        rag_available=True,
        public_url="https://github.com/awsdocs/aws-doc-sdk-examples.git",
        license="Apache-2.0",
    ),
}


def repository_catalog() -> List[dict]:
    """Return JSON-safe repository metadata in stable display order."""

    return [asdict(REPOSITORIES[key]) for key in ("generic", "ledgerflow", "aws_s3")]


def repository_spec(repository_id: str) -> RepositorySpec:
    try:
        return REPOSITORIES[repository_id]
    except KeyError as exc:
        raise ValueError(f"Unknown repository_id: {repository_id}") from exc


def repository_path(
    repository_id: str,
    *,
    config: AppConfig = CONFIG,
    project_root: str | Path | None = None,
) -> Optional[Path]:
    spec = repository_spec(repository_id)
    if spec.relative_path is None:
        return None
    root = Path(project_root or config.storage.drive_project_root)
    return root / spec.relative_path


def repository_index_dirs(
    repository_id: str,
    *,
    config: AppConfig = CONFIG,
    project_root: str | Path | None = None,
) -> tuple[Path, Path]:
    if repository_id == "generic":
        raise ValueError("The generic/no-RAG catalogue entry has no repository index.")
    root = Path(project_root or config.storage.drive_project_root)
    base = root / "outputs" / "repositories" / repository_id
    return base / "parsed", base / "embeddings"


def _git(args: List[str], *, cwd: Path | None = None) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(cwd) if cwd else None,
        check=True,
        text=True,
        capture_output=True,
        timeout=600,
    )
    return completed.stdout.strip()


def prepare_public_repository(
    repository_id: str = "aws_s3",
    *,
    config: AppConfig = CONFIG,
    project_root: str | Path | None = None,
) -> Path:
    """Download/reuse a public demo repository without overwriting anything.

    The operation is idempotent.  An existing valid checkout is reused.  An
    existing incomplete directory fails closed so user files are never
    deleted automatically.
    """

    spec = repository_spec(repository_id)
    if not spec.public_url:
        path = repository_path(repository_id, config=config, project_root=project_root)
        if path is None or not path.is_dir():
            raise FileNotFoundError(f"Bundled repository is missing: {path}")
        return path

    destination = repository_path(repository_id, config=config, project_root=project_root)
    assert destination is not None
    required = (
        destination / "python" / "example_code" / "s3",
        destination / "javav2" / "example_code" / "s3",
    )
    if destination.exists():
        if (destination / ".git").is_dir() and all(path.is_dir() for path in required):
            return destination
        raise RuntimeError(
            f"Public repository directory exists but is incomplete: {destination}. "
            "Move it aside manually, then run preparation again."
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    _git(["clone", "--filter=blob:none", "--no-checkout", spec.public_url, str(destination)])
    _git(["sparse-checkout", "init", "--cone"], cwd=destination)
    _git(
        [
            "sparse-checkout",
            "set",
            "python/example_code/s3",
            "javav2/example_code/s3",
        ],
        cwd=destination,
    )
    _git(["checkout", "main"], cwd=destination)
    commit = _git(["rev-parse", "HEAD"], cwd=destination)
    provenance = (
        f"repository={spec.public_url}\n"
        f"commit={commit}\n"
        "subtrees=python/example_code/s3,javav2/example_code/s3\n"
        f"license={spec.license}\n"
    )
    (destination / "REPOCODER_PROVENANCE.txt").write_text(provenance, encoding="utf-8")
    return destination


def auto_download_enabled() -> bool:
    return os.environ.get("REPOCODER_AUTO_DOWNLOAD_PUBLIC_REPOS", "true").lower() == "true"

