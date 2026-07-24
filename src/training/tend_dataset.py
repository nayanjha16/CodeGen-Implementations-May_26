"""Build HuggingFace SFT datasets from the published TEND HF corpus."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from src.datasets.tend_loader import TENDLoader
from src.training.filters import FilterStats, filter_tend_rows, log_filter_stats
from src.training.prompt_factory import build_training_prompt, build_training_target
from src.training.tasks import (
    DEFAULT_EVAL_SPLIT,
    DEFAULT_TRAINING_SPLIT,
    get_eval_dataset_configs,
    get_training_dataset_configs,
)
from src.training.token_stats import TokenStats, log_token_stats
from src.utils.config import get_model_name, get_training_config, load_config

logger = logging.getLogger("codegen.training")

# TRL appends EOS during dataset preparation; reserve one slot in the token budget.
_EOS_TOKEN_RESERVE = 1


@dataclass
class SFTBuildResult:
    """HuggingFace dataset plus builder metadata."""

    dataset: Any
    filter_stats: dict[str, Any]
    token_stats: dict[str, Any]
    task: str
    row_count: int


def load_tend_rows(
    *,
    configs: tuple[str, ...] | list[str] | None = None,
    split: str = DEFAULT_TRAINING_SPLIT,
    config: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Load and concatenate TEND rows from one or more HF dataset configs."""
    cfg = config or load_config()
    subset_names = tuple(configs) if configs is not None else get_training_dataset_configs(cfg)
    rows: list[dict[str, str]] = []

    for subset in subset_names:
        loader = TENDLoader(config=subset)
        subset_rows = loader.load_split(split)
        rows.extend(subset_rows)
        logger.info(
            "Loaded TEND %s/%s (%d rows)",
            subset,
            split,
            len(subset_rows),
        )

    logger.info(
        "Combined TEND rows: configs=%s split=%s total=%d",
        subset_names,
        split,
        len(rows),
    )
    return rows


def load_tend_training_rows(config: dict[str, Any] | None = None) -> list[dict[str, str]]:
    """Load spider + bird train rows for LoRA fine-tuning."""
    cfg = config or load_config()
    training_cfg = get_training_config(cfg)
    split = str(training_cfg.get("split", DEFAULT_TRAINING_SPLIT))
    return load_tend_rows(configs=get_training_dataset_configs(cfg), split=split, config=cfg)


def load_tend_eval_rows(config: dict[str, Any] | None = None) -> list[dict[str, str]]:
    """Load spider + bird test rows for held-out eval during training."""
    cfg = config or load_config()
    training_cfg = get_training_config(cfg)
    split = str(training_cfg.get("eval_split", DEFAULT_EVAL_SPLIT))
    configs = get_eval_dataset_configs(cfg)
    return load_tend_rows(configs=configs, split=split, config=cfg)


def _resolve_tokenizer(config: dict[str, Any], tokenizer: Any | None = None):
    if tokenizer is not None:
        return tokenizer

    from src.models.model_loader import (
        ensure_model_cached,
        hf_load_kwargs,
        is_codegen2_model,
        _load_codegen2_tokenizer,
    )

    model_name = get_model_name(config)
    local_path = ensure_model_cached(model_name)
    load_kwargs = hf_load_kwargs(model_name, config, local_files_only=True)
    if is_codegen2_model(model_name):
        return _load_codegen2_tokenizer(local_path, **load_kwargs)

    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(local_path, **load_kwargs)


def _truncate_prompt_tokens(
    prompt: str,
    target: str,
    tokenizer,
    *,
    max_length: int,
    max_target_tokens: int,
    token_stats: TokenStats,
) -> tuple[str, str] | None:
    """Return (truncated_prompt, prompt+target) or None when the row is too long."""
    target_ids = tokenizer.encode(target, add_special_tokens=False)
    if len(target_ids) > max_target_tokens:
        token_stats.skipped_too_long_target += 1
        return None

    prompt_budget = max_length - len(target_ids) - _EOS_TOKEN_RESERVE
    if prompt_budget <= 0:
        token_stats.skipped_too_long_target += 1
        return None

    prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
    if len(prompt_ids) > prompt_budget:
        prompt_ids = prompt_ids[-prompt_budget:]
        prompt = tokenizer.decode(prompt_ids, skip_special_tokens=True)

    text = f"{prompt}{target}"
    total_tokens = len(tokenizer.encode(text, add_special_tokens=False))
    token_stats.record(
        prompt_tokens=len(prompt_ids),
        target_tokens=len(target_ids),
        total_tokens=total_tokens,
    )
    return prompt, text


def build_sft_examples(
    rows: list[dict[str, str]],
    task: str,
    *,
    config: dict[str, Any] | None = None,
    tokenizer: Any | None = None,
    max_samples: int | None = None,
    filter_stats: FilterStats | None = None,
    token_stats: TokenStats | None = None,
) -> tuple[list[dict[str, str]], FilterStats, TokenStats]:
    """Convert TEND rows into `(prompt, target, text)` training examples."""
    cfg = config or load_config()
    training_cfg = get_training_config(cfg)
    max_length = int(training_cfg.get("max_length", 2048))
    max_target_tokens = int(training_cfg.get("max_target_tokens", 256))

    filtered_rows = filter_tend_rows(rows, task, stats=filter_stats)
    if max_samples is not None:
        filtered_rows = filtered_rows[: max(0, max_samples)]

    tok = _resolve_tokenizer(cfg, tokenizer)
    # We enforce max_length ourselves; avoid spurious warnings on long raw prompts.
    tok.model_max_length = max(int(tok.model_max_length or 0), max_length * 4)
    stats = filter_stats or FilterStats()
    tokens = token_stats or TokenStats()

    examples: list[dict[str, str]] = []
    for row in filtered_rows:
        raw_prompt = build_training_prompt(row, task, config=cfg)
        target = build_training_target(row, task)
        truncated = _truncate_prompt_tokens(
            raw_prompt,
            target,
            tok,
            max_length=max_length,
            max_target_tokens=max_target_tokens,
            token_stats=tokens,
        )
        if truncated is None:
            stats.record_skip("sequence_too_long")
            continue

        prompt, text = truncated
        examples.append(
            {
                "id": row.get("id", ""),
                "task": task,
                "prompt": prompt,
                "target": target,
                "text": text,
                "source_dataset": row.get("source_dataset", ""),
            }
        )

    return examples, stats, tokens


def build_sft_dataset(
    rows: list[dict[str, str]] | None = None,
    task: str = "text2sql",
    *,
    config: dict[str, Any] | None = None,
    split: str | None = None,
    tokenizer: Any | None = None,
    max_samples: int | None = None,
):
    """Build a HuggingFace Dataset with a `text` column for SFT training."""
    from datasets import Dataset

    cfg = config or load_config()
    if rows is None:
        if split == "test" or split == DEFAULT_EVAL_SPLIT:
            rows = load_tend_eval_rows(cfg)
        else:
            rows = load_tend_training_rows(cfg)

    logger.info("[%s] Building SFT dataset from %d source rows", task, len(rows))
    filter_stats = FilterStats()
    examples, filter_stats, token_stats = build_sft_examples(
        rows,
        task,
        config=cfg,
        tokenizer=tokenizer,
        max_samples=max_samples,
        filter_stats=filter_stats,
        token_stats=TokenStats(),
    )

    log_filter_stats(task, filter_stats)
    log_token_stats(task, token_stats)
    logger.info("[%s] SFT dataset ready: %d examples", task, len(examples))

    dataset = Dataset.from_list(examples)
    return SFTBuildResult(
        dataset=dataset,
        filter_stats=filter_stats.to_dict(),
        token_stats=token_stats.to_dict(),
        task=task,
        row_count=len(examples),
    )
