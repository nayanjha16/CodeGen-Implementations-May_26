"""LoRA fine-tuning orchestration via TRL SFTTrainer."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.training.collator import prepare_prompt_completion_dataset
from src.training.lora_config import build_lora_config
from src.training.mlflow_utils import TrainingMLflowLogger
from src.training.tend_dataset import build_sft_dataset, load_tend_eval_rows, load_tend_training_rows
from src.utils.config import get_adapter_path, get_model_name, get_training_config, load_config
from src.utils.logging import log_step, setup_logging, task_label
from src.utils.paths import resolve_adapter_run_name
from src.utils.device import is_cpu_device, resolve_device, supports_dataloader_pin_memory
from src.utils.seeds import set_seeds

logger = logging.getLogger("codegen.training")


@dataclass
class TrainLoraResult:
    """Summary of a completed LoRA training run."""

    task: str
    output_dir: Path
    checkpoint_run: str
    train_rows: int
    eval_rows: int
    train_loss: float | None
    eval_loss: float | None
    best_eval_loss: float | None
    train_runtime: float | None
    mlflow_run_id: str | None
    metadata_path: Path


def _load_rows_from_path(path: str | Path) -> list[dict[str, str]]:
    """Load TEND-style rows from CSV or JSONL."""
    from src.datasets.tend_loader import TENDLoader

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Training data file not found: {file_path}")

    if file_path.suffix.lower() == ".jsonl":
        rows: list[dict[str, str]] = []
        with file_path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                rows.append(TENDLoader.standardize(row))
        return rows

    if file_path.suffix.lower() == ".csv":
        import pandas as pd

        df = pd.read_csv(file_path)
        rows = []
        for raw in df.to_dict(orient="records"):
            normalized = dict(raw)
            if "schema" in normalized and "sql_schema" not in normalized:
                normalized["sql_schema"] = normalized["schema"]
            if "sql" in normalized and "sql_query" not in normalized:
                normalized["sql_query"] = normalized["sql"]
            rows.append(TENDLoader.standardize(normalized))
        return rows

    raise ValueError(f"Unsupported training data format: {file_path.suffix}")


def _resolve_train_rows(
    train_csv: str | Path | None,
    config: dict[str, Any],
) -> list[dict[str, str]]:
    if train_csv is not None:
        return _load_rows_from_path(train_csv)
    return load_tend_training_rows(config)


def _resolve_eval_rows(
    eval_csv: str | Path | None,
    config: dict[str, Any],
) -> list[dict[str, str]] | None:
    if eval_csv is not None:
        return _load_rows_from_path(eval_csv)
    return load_tend_eval_rows(config)


def _ensure_tokenizer_pad_token(tokenizer: Any) -> None:
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id


def _build_sft_config(
    output_dir: Path,
    training_cfg: dict[str, Any],
    *,
    epochs: int | None = None,
    max_samples: int | None = None,
    device: str,
    skip_eval: bool = False,
) -> Any:
    from trl import SFTConfig

    per_device_train_batch_size = int(training_cfg.get("per_device_train_batch_size", 8))
    if max_samples is not None and max_samples <= 8:
        per_device_train_batch_size = min(per_device_train_batch_size, max(1, max_samples))

    return SFTConfig(
        output_dir=str(output_dir),
        num_train_epochs=float(epochs or training_cfg.get("epochs", 5)),
        per_device_train_batch_size=per_device_train_batch_size,
        per_device_eval_batch_size=int(training_cfg.get("per_device_eval_batch_size", 8)),
        gradient_accumulation_steps=int(training_cfg.get("gradient_accumulation_steps", 4)),
        learning_rate=float(training_cfg.get("learning_rate", 2e-4)),
        weight_decay=float(training_cfg.get("weight_decay", 0.01)),
        warmup_ratio=float(training_cfg.get("warmup_ratio", 0.05)),
        lr_scheduler_type=str(training_cfg.get("lr_scheduler_type", "cosine")),
        max_grad_norm=float(training_cfg.get("max_grad_norm", 1.0)),
        fp16=bool(training_cfg.get("fp16", False)),
        bf16=bool(training_cfg.get("bf16", False)),
        max_length=int(training_cfg.get("max_length", 2048)),
        truncation_mode="keep_start",
        completion_only_loss=True,
        loss_type="chunked_nll",
        dataset_text_field="text",
        logging_steps=10,
        logging_dir=str(output_dir / "logs"),
        save_strategy="epoch",
        eval_strategy="no" if skip_eval else "epoch",
        load_best_model_at_end=not skip_eval,
        metric_for_best_model="eval_loss" if not skip_eval else None,
        greater_is_better=False if not skip_eval else None,
        save_total_limit=1,
        report_to="none",
        seed=int((training_cfg.get("seed") or 42)),
        use_cpu=is_cpu_device(device),
        dataloader_pin_memory=supports_dataloader_pin_memory(device),
    )


def _write_run_metadata(
    path: Path,
    *,
    task: str,
    model_name: str,
    device: str,
    checkpoint_run: str,
    output_dir: Path,
    train_rows: int,
    eval_rows: int,
    train_loss: float | None,
    eval_loss: float | None,
    best_eval_loss: float | None,
    train_runtime: float | None,
    mlflow_run_id: str | None,
    filter_stats: dict[str, Any],
    token_stats: dict[str, Any],
    log_history: list[dict[str, Any]] | None = None,
) -> Path:
    metadata = {
        "task": task,
        "model_name": model_name,
        "device": device,
        "checkpoint_run": checkpoint_run,
        "adapter_path": str(output_dir),
        "train_rows": train_rows,
        "eval_rows": eval_rows,
        "train_loss": train_loss,
        "eval_loss": eval_loss,
        "best_eval_loss": best_eval_loss,
        "train_runtime_seconds": train_runtime,
        "mlflow_run_id": mlflow_run_id,
        "filter_stats": filter_stats,
        "token_stats": token_stats,
        "log_history": log_history or [],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return path


def train_lora(
    task: str,
    *,
    config: dict[str, Any] | None = None,
    train_rows: list[dict[str, str]] | None = None,
    eval_rows: list[dict[str, str]] | None = None,
    train_csv: str | Path | None = None,
    eval_csv: str | Path | None = None,
    output_dir: str | Path | None = None,
    run: str | None = None,
    max_samples: int | None = None,
    device: str | None = None,
    epochs: int | None = None,
    enable_mlflow: bool = True,
    skip_eval: bool = False,
) -> TrainLoraResult:
    """Train a LoRA adapter for one task and save adapter weights to output_dir."""
    from transformers import AutoModelForCausalLM
    from trl import SFTTrainer

    from src.models.model_loader import ensure_model_cached, is_seq2seq_model, load_tokenizer

    setup_logging()
    cfg = config or load_config()
    set_seeds(cfg)

    training_cfg = get_training_config(cfg)
    model_name = get_model_name(cfg)
    if is_seq2seq_model(model_name):
        raise ValueError(f"{model_name} is seq2seq; causal LM training only.")

    resolved_output = (
        Path(output_dir)
        if output_dir is not None
        else get_adapter_path(task, cfg, run=run)
    )
    checkpoint_run = resolve_adapter_run_name(run)
    resolved_output.mkdir(parents=True, exist_ok=True)

    resolved_device = resolve_device(device or cfg.get("model", {}).get("device", "auto"))
    logger.info(
        "=== LoRA training [%s] === model=%s device=%s output=%s",
        task_label(task),
        model_name,
        resolved_device,
        resolved_output,
    )

    log_step(task, "Loading training data")
    train_rows = train_rows if train_rows is not None else _resolve_train_rows(train_csv, cfg)
    if skip_eval:
        eval_rows_raw = None
    elif eval_rows is not None:
        eval_rows_raw = eval_rows
    else:
        eval_rows_raw = _resolve_eval_rows(eval_csv, cfg)

    log_step(task, "Building SFT train dataset")
    train_result = build_sft_dataset(
        rows=train_rows,
        task=task,
        config=cfg,
        max_samples=max_samples,
    )
    if train_result.row_count == 0:
        raise ValueError(f"No training examples built for task '{task}'.")

    eval_dataset = None
    eval_row_count = 0
    if eval_rows_raw is not None:
        log_step(task, "Building SFT eval dataset")
        eval_build = build_sft_dataset(
            rows=eval_rows_raw,
            task=task,
            config=cfg,
            max_samples=max_samples,
        )
        eval_row_count = eval_build.row_count
        if eval_row_count > 0:
            eval_dataset = prepare_prompt_completion_dataset(eval_build.dataset, task)

    train_dataset = prepare_prompt_completion_dataset(train_result.dataset, task)
    logger.info(
        "[%s] Dataset ready: train=%d eval=%d",
        task_label(task),
        train_result.row_count,
        eval_row_count,
    )

    log_step(task, "Loading base model weights")
    local_path = ensure_model_cached(model_name)
    tokenizer = load_tokenizer(model_name, cfg)
    _ensure_tokenizer_pad_token(tokenizer)

    model = AutoModelForCausalLM.from_pretrained(local_path, local_files_only=True)
    if tokenizer.pad_token_id is not None:
        model.config.pad_token_id = tokenizer.pad_token_id
    if tokenizer.bos_token_id is not None:
        model.config.bos_token_id = tokenizer.bos_token_id
    if not is_cpu_device(resolved_device):
        model = model.to(resolved_device)

    peft_config = build_lora_config(cfg)
    sft_args = _build_sft_config(
        resolved_output,
        training_cfg,
        epochs=epochs,
        max_samples=max_samples,
        device=resolved_device,
        skip_eval=skip_eval or eval_dataset is None,
    )

    trainer = SFTTrainer(
        model=model,
        args=sft_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        processing_class=tokenizer,
        peft_config=peft_config,
    )

    log_step(
        task,
        "Starting SFT training (epochs=%s, batch=%s, grad_accum=%s)",
        sft_args.num_train_epochs,
        sft_args.per_device_train_batch_size,
        sft_args.gradient_accumulation_steps,
    )
    train_output = trainer.train()
    trainer.save_model(str(resolved_output))

    train_loss = getattr(train_output, "training_loss", None)
    train_runtime = None
    if getattr(train_output, "metrics", None):
        train_runtime = train_output.metrics.get("train_runtime")

    eval_loss = None
    best_eval_loss = None
    if eval_dataset is not None:
        log_step(task, "Running final eval pass")
        eval_metrics = trainer.evaluate()
        eval_loss = eval_metrics.get("eval_loss")
        best_eval_loss = trainer.state.best_metric
        if best_eval_loss is None and eval_loss is not None:
            best_eval_loss = float(eval_loss)

    log_history = list(trainer.state.log_history) if trainer.state.log_history else []

    mlflow_run_id: str | None = None
    if enable_mlflow:
        metrics: dict[str, float] = {}
        if train_loss is not None:
            metrics["train_loss"] = float(train_loss)
        if eval_loss is not None:
            metrics["eval_loss"] = float(eval_loss)
        if best_eval_loss is not None:
            metrics["best_eval_loss"] = float(best_eval_loss)

        mlflow_logger = TrainingMLflowLogger(cfg)
        mlflow_run_id = mlflow_logger.log_training_run(
            task=task,
            model_name=model_name,
            output_dir=str(resolved_output),
            train_rows=train_result.row_count,
            eval_rows=eval_row_count,
            hyperparams={
                "learning_rate": sft_args.learning_rate,
                "epochs": sft_args.num_train_epochs,
                "per_device_train_batch_size": sft_args.per_device_train_batch_size,
                "gradient_accumulation_steps": sft_args.gradient_accumulation_steps,
                "lora_r": peft_config.r,
                "lora_alpha": peft_config.lora_alpha,
            },
            metrics=metrics,
        )

    metadata_path = _write_run_metadata(
        resolved_output / "run_metadata.json",
        task=task,
        model_name=model_name,
        device=resolved_device,
        checkpoint_run=checkpoint_run,
        output_dir=resolved_output,
        train_rows=train_result.row_count,
        eval_rows=eval_row_count,
        train_loss=train_loss,
        eval_loss=eval_loss,
        best_eval_loss=best_eval_loss,
        train_runtime=float(train_runtime) if train_runtime is not None else None,
        mlflow_run_id=mlflow_run_id,
        filter_stats=train_result.filter_stats,
        token_stats=train_result.token_stats,
        log_history=log_history,
    )

    adapter_config = resolved_output / "adapter_config.json"
    adapter_weights = resolved_output / "adapter_model.safetensors"
    if not adapter_config.exists():
        raise FileNotFoundError(f"Missing adapter config after training: {adapter_config}")
    if not adapter_weights.exists():
        raise FileNotFoundError(f"Missing adapter weights after training: {adapter_weights}")

    logger.info(
        "=== LoRA training complete [%s] train_loss=%s eval_loss=%s best_eval=%s adapter=%s",
        task_label(task),
        train_loss,
        eval_loss,
        best_eval_loss,
        resolved_output,
    )

    return TrainLoraResult(
        task=task,
        output_dir=resolved_output,
        checkpoint_run=checkpoint_run,
        train_rows=train_result.row_count,
        eval_rows=eval_row_count,
        train_loss=train_loss,
        eval_loss=eval_loss,
        best_eval_loss=best_eval_loss,
        train_runtime=float(train_runtime) if train_runtime is not None else None,
        mlflow_run_id=mlflow_run_id,
        metadata_path=metadata_path,
    )
