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

from pathlib import Path
from typing import Optional

from src.config import CONFIG, AppConfig
from src.logger import LOG, SectionPrinter, SummaryPrinter


class CheckpointManager:
    """
    Manages training checkpoint paths and resume behavior.
    """

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.checkpoint_dir = (
            config.storage.project_root()
            / config.storage.checkpoints_dir
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

    def should_resume(self) -> Optional[str]:
        """
        Returns latest checkpoint if auto-resume is enabled.
        """

        if not self.config.training.auto_resume_from_checkpoint:
            return None

        latest = self.latest_checkpoint()

        if latest:
            LOG.info(f"Found checkpoint for resume: {latest}")
            return latest

        LOG.info("No checkpoint found. Training will start fresh.")
        return None

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
