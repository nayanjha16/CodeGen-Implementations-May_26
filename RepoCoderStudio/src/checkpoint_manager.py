"""
============================================================
RepoCoder Studio
checkpoint_manager.py
============================================================

Checkpoint Manager for Colab-safe LoRA training.

Purpose
-------
Training checkpoints must be stored in Google Drive so runtime
disconnects do not destroy progress.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional

from src.config import CONFIG, AppConfig
from src.logger import LOG, SectionPrinter, SummaryPrinter
from src.artifact_manifest import file_sha256
from src.normalization_engine import NORMALIZER_VERSION


class CheckpointManager:
    """
    Manages training checkpoint paths and resume behavior.
    """

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.checkpoint_root = (
            config.storage.project_root()
            / config.storage.checkpoints_dir
        )
        task_dataset_path = (
            config.storage.project_root()
            / config.storage.task_datasets_dir
            / config.training.task_dataset_filename
        )
        self.task_dataset_path = task_dataset_path
        self._task_dataset_sha256 = (
            file_sha256(task_dataset_path) if task_dataset_path.exists() else None
        )
        fingerprint = json.dumps(
            self.current_manifest(),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        fingerprint_short = hashlib.sha256(fingerprint).hexdigest()[:12]
        self.checkpoint_dir = (
            self.checkpoint_root
            / (
                f"{config.experiment.training_manifest_version}_"
                f"{config.runtime.run_mode}_{fingerprint_short}"
            )
        )
        self.adapter_dir = (
            config.storage.project_root()
            / config.storage.adapters_dir
            / config.training.final_adapter_name
        )

        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.adapter_dir.parent.mkdir(parents=True, exist_ok=True)

    def latest_checkpoint(self) -> Optional[str]:
        """
        Finds the latest Hugging Face checkpoint folder.

        Returns
        -------
        Optional[str]
            Path string or None.
        """

        checkpoints = list(self.checkpoint_dir.glob("checkpoint-*"))

        if not checkpoints:
            return None

        def step_num(path: Path):
            try:
                return int(path.name.split("-")[-1])
            except Exception:
                return -1

        latest = sorted(checkpoints, key=step_num)[-1]

        return str(latest)

    def manifest_path(self) -> Path:
        """
        Path to the manifest recording which prompt/task-contract version
        the checkpoints in checkpoint_dir were produced under.
        """

        return self.checkpoint_dir / "training_manifest.json"

    def current_manifest(self) -> Dict[str, Any]:
        """
        Version fingerprint for the run about to train/resume.

        The data profile and effective training settings are part of the
        fingerprint. This prevents a checkpoint produced by the old 300-row
        demo from being silently resumed by the 1,200-row capstone run.
        """

        return {
            "training_manifest_version": self.config.experiment.training_manifest_version,
            "task_contract_version": self.config.experiment.task_contract_version,
            "prompt_version": self.config.experiment.prompt_version,
            "student_model_name": self.config.models.student_model_name,
            "run_mode": self.config.runtime.run_mode,
            "random_seed": self.config.runtime.random_seed,
            "task_dataset_sha256": self._task_dataset_sha256,
            "task_dataset_filename": self.config.training.task_dataset_filename,
            "final_adapter_name": self.config.training.final_adapter_name,
            "normalizer_version": NORMALIZER_VERSION,
            "completion_termination": "supervised_eos_v1",
            "split_limits": {
                split: self.config.dataset.get_split_limit(
                    split=split,
                    run_mode=self.config.runtime.run_mode,
                )
                for split in ("train", "validation", "test")
            },
            "training": {
                "epochs": (
                    self.config.training.num_train_epochs_demo
                    if self.config.runtime.run_mode == "demo"
                    else (
                        self.config.training.num_train_epochs_capstone
                        if self.config.runtime.run_mode == "capstone"
                        else self.config.training.num_train_epochs_full
                    )
                ),
                "learning_rate": self.config.training.learning_rate,
                "batch_size": self.config.training.per_device_train_batch_size,
                "gradient_accumulation_steps": (
                    self.config.training.gradient_accumulation_steps
                ),
                "lora_rank": self.config.training.lora_rank,
                "lora_alpha": self.config.training.lora_alpha,
                "lora_dropout": self.config.training.lora_dropout,
                "max_seq_length": self.config.models.max_seq_length,
            },
        }

    def write_manifest(self):
        """
        Records the current version fingerprint alongside the checkpoints.
        """

        with self.manifest_path().open("w", encoding="utf-8") as f:
            json.dump(self.current_manifest(), f, indent=2)

    def checkpoint_matches_manifest(self) -> bool:
        """
        Whether the existing checkpoints were produced under the same
        prompt/task-contract version and base model as the current config.

        A missing manifest means the checkpoint predates this check (or was
        produced by an incompatible run) and is treated as a mismatch, since
        compatibility cannot be verified.
        """

        path = self.manifest_path()
        if not path.exists():
            return False

        try:
            with path.open("r", encoding="utf-8") as f:
                saved = json.load(f)
        except (json.JSONDecodeError, OSError):
            return False

        return saved == self.current_manifest()

    def should_resume(self) -> Optional[str]:
        """
        Returns latest checkpoint if auto-resume is enabled and the
        checkpoint is compatible with the current prompt/task-contract
        version. Incompatible or unverifiable checkpoints are ignored so
        stale-format checkpoints do not get silently resumed (task
        interference) or unpickled from an untrusted/mismatched state.
        """

        if not self.config.training.auto_resume_from_checkpoint:
            return None

        latest = self.latest_checkpoint()

        if not latest:
            LOG.info("No checkpoint found. Training will start fresh.")
            return None

        if not self.checkpoint_matches_manifest():
            LOG.warning(
                f"Checkpoint '{latest}' does not match the current "
                f"{self.config.experiment.task_contract_version} / "
                f"{self.config.experiment.prompt_version} version. "
                "Ignoring it and starting fresh to avoid task interference."
            )
            return None

        LOG.info(f"Found checkpoint for resume: {latest}")
        return latest

    def training_output_dir(self) -> str:
        """
        Returns checkpoint output directory for Trainer.
        """

        return str(self.checkpoint_dir)

    def final_adapter_dir(self) -> str:
        """
        Returns final adapter save directory.
        """

        return str(self.adapter_dir)

    def print_status(self):
        """
        Prints checkpoint status.
        """

        latest = self.latest_checkpoint()

        SummaryPrinter.print_summary(
            "Checkpoint Manager Summary",
            {
                "Checkpoint Dir": str(self.checkpoint_dir),
                "Latest Checkpoint": latest if latest else "None",
                "Final Adapter Dir": str(self.adapter_dir),
            },
        )
