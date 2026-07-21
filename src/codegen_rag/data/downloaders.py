"""Dataset downloaders for CoDocBench, Spider, BirdBench, CodeParrot, and Rust repos.

Every downloader is idempotent: if the target already exists on disk (Drive,
in Colab) it is skipped, which is what lets notebooks be re-run from the top
without re-downloading gigabytes of data every session.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from codegen_rag.utils.logging_config import get_logger

logger = get_logger(__name__)


class DownloadError(RuntimeError):
    """Raised when a dataset cannot be fetched after retries."""


def _run_git_clone(repo_url: str, target_dir: Path, depth: int = 1) -> None:
    if target_dir.exists() and any(target_dir.iterdir()):
        logger.info("Skipping clone, already present: %s", target_dir)
        return
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["git", "clone", "--depth", str(depth), repo_url, str(target_dir)]
    logger.info("Cloning %s -> %s", repo_url, target_dir)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise DownloadError(f"git clone failed for {repo_url}: {result.stderr}")


def download_codocbench(target_dir: Path, repo_url: str) -> Path:
    """Clone CoDocBench (code-documentation pairs across languages)."""
    _run_git_clone(repo_url, target_dir)
    return target_dir


def download_spider(target_dir: Path, hf_dataset: str = "xlangai/spider") -> Any:
    """Download the Spider text-to-SQL dataset via the HuggingFace mirror."""
    from datasets import load_dataset

    marker = target_dir / ".complete"
    if marker.exists():
        logger.info("Spider already downloaded at %s", target_dir)
        return load_dataset(hf_dataset, trust_remote_code=True)

    target_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Downloading Spider from HuggingFace: %s", hf_dataset)
    ds = load_dataset(hf_dataset, trust_remote_code=True)
    ds.save_to_disk(str(target_dir))
    marker.write_text("ok")
    return ds


def download_birdbench(target_dir: Path, hf_dataset: str = "birdsql/bird") -> Any:
    """Download the BirdBench text-to-SQL dataset via the HuggingFace mirror."""
    from datasets import load_dataset

    marker = target_dir / ".complete"
    if marker.exists():
        logger.info("BirdBench already downloaded at %s", target_dir)
        return load_dataset(hf_dataset, trust_remote_code=True)

    target_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Downloading BirdBench from HuggingFace: %s", hf_dataset)
    try:
        ds = load_dataset(hf_dataset, trust_remote_code=True)
    except Exception as exc:  # pragma: no cover - network dependent
        raise DownloadError(
            f"Could not download BirdBench from '{hf_dataset}'. "
            f"Verify dataset availability at https://bird-bench.github.io/. Original error: {exc}"
        ) from exc
    ds.save_to_disk(str(target_dir))
    marker.write_text("ok")
    return ds


def download_codeparrot_subset(
    target_dir: Path,
    languages: list[str],
    max_samples: int,
    hf_dataset: str = "codeparrot/github-code",
) -> list[dict[str, Any]]:
    """Stream a bounded subset of CodeParrot for a set of languages.

    CodeParrot is enormous (>1TB uncompressed), so we always use ``streaming=True``
    and cap the number of samples per language via ``max_samples``.
    """
    from datasets import load_dataset

    marker = target_dir / ".complete"
    if marker.exists():
        from codegen_rag.utils.io_utils import read_jsonl

        logger.info("CodeParrot subset already cached at %s", target_dir)
        return read_jsonl(target_dir / "samples.jsonl")

    target_dir.mkdir(parents=True, exist_ok=True)
    samples: list[dict[str, Any]] = []
    per_language_cap = max(1, max_samples // max(len(languages), 1))

    for lang in languages:
        logger.info("Streaming CodeParrot subset for language=%s (cap=%d)", lang, per_language_cap)
        stream = load_dataset(hf_dataset, streaming=True, split="train", languages=[lang], trust_remote_code=True)
        count = 0
        for row in stream:
            samples.append(
                {
                    "language": lang,
                    "code": row.get("code", ""),
                    "path": row.get("path", ""),
                    "repo_name": row.get("repo_name", ""),
                }
            )
            count += 1
            if count >= per_language_cap:
                break

    from codegen_rag.utils.io_utils import write_jsonl

    write_jsonl(samples, target_dir / "samples.jsonl")
    marker.write_text("ok")
    logger.info("Cached %d CodeParrot samples across %d languages", len(samples), len(languages))
    return samples


def download_rust_corpus(
    target_dir: Path,
    min_samples: int,
    max_samples: int,
    hf_dataset: str = "codeparrot/github-code",
    language_filter: str = "Rust",
) -> list[dict[str, Any]]:
    """Download a bounded Rust code corpus for Task 4 (new-language fine-tuning)."""
    from datasets import load_dataset

    marker = target_dir / ".complete"
    if marker.exists():
        from codegen_rag.utils.io_utils import read_jsonl

        logger.info("Rust corpus already cached at %s", target_dir)
        return read_jsonl(target_dir / "rust_samples.jsonl")

    target_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Streaming Rust corpus (target=%d-%d samples)", min_samples, max_samples)
    stream = load_dataset(hf_dataset, streaming=True, split="train", languages=[language_filter], trust_remote_code=True)

    samples: list[dict[str, Any]] = []
    for row in stream:
        code = row.get("code", "")
        if not code or len(code) < 20:
            continue
        samples.append(
            {
                "language": "rust",
                "code": code,
                "path": row.get("path", ""),
                "repo_name": row.get("repo_name", ""),
            }
        )
        if len(samples) >= max_samples:
            break

    if len(samples) < min_samples:
        logger.warning(
            "Only collected %d Rust samples (< min_samples=%d). Proceeding anyway; "
            "consider raising max_samples or adding another source.",
            len(samples),
            min_samples,
        )

    from codegen_rag.utils.io_utils import write_jsonl

    write_jsonl(samples, target_dir / "rust_samples.jsonl")
    marker.write_text("ok")
    logger.info("Cached %d Rust samples", len(samples))
    return samples


def download_all(settings) -> dict[str, Any]:  # noqa: ANN001 - Settings imported lazily to avoid cycle
    """Convenience entry point: download every dataset needed up through the
    current checkpoint. Individual downloaders are idempotent, so re-running
    this is always safe.
    """
    data_cfg = settings.data
    results: dict[str, Any] = {}

    codoc_cfg = data_cfg.get("codocbench", {})
    results["codocbench"] = download_codocbench(
        settings.resolve_path(codoc_cfg.get("clone_dir", "data/raw/codocbench")),
        codoc_cfg.get("repo_url", "https://github.com/kunpai/codocbench"),
    )

    rust_cfg = data_cfg.get("rust_corpus", {})
    results["rust_corpus"] = download_rust_corpus(
        settings.resolve_path(rust_cfg.get("clone_dir", "data/raw/rust_corpus")),
        min_samples=rust_cfg.get("min_samples", 500),
        max_samples=rust_cfg.get("max_samples", 5000),
        hf_dataset=rust_cfg.get("hf_dataset", "codeparrot/github-code"),
        language_filter=rust_cfg.get("language_filter", "Rust"),
    )

    logger.info("download_all() complete: %s", list(results.keys()))
    return results
