"""Checkpoint save/resume management for training runs.

Handles the "resume checkpoints" requirement from the project brief: every
training script calls :meth:`CheckpointManager.find_resume_point` before
starting so a Colab disconnect never means starting over.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from codegen_rag.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class CheckpointMeta:
    step: int
    epoch: int
    loss: float
    best_loss: float
    checkpoint_dir: str


class CheckpointManager:
    """Manages a directory of numbered checkpoints plus a `latest`/`best` pointer.

    ``save_total_limit`` bounds disk usage (Drive quota is a real constraint on
    Colab's free tier): after every save, checkpoint directories beyond the
    limit are deleted, always preserving the ``best`` and ``latest`` pointers
    even if they'd otherwise be pruned.
    """

    def __init__(self, root: Path, save_total_limit: int = 2):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.state_file = self.root / "training_state.json"
        self.save_total_limit = save_total_limit

    def save(self, model: Any, step: int, epoch: int, loss: float) -> CheckpointMeta:
        ckpt_dir = self.root / f"checkpoint-{step:06d}"
        ckpt_dir.mkdir(parents=True, exist_ok=True)
        model.save_pretrained(ckpt_dir)

        state = self._load_state()
        best_loss = min(loss, state.get("best_loss", float("inf")))
        meta = CheckpointMeta(
            step=step, epoch=epoch, loss=loss, best_loss=best_loss, checkpoint_dir=str(ckpt_dir)
        )

        state["latest"] = asdict(meta)
        if loss <= best_loss:
            state["best"] = asdict(meta)
        state["best_loss"] = best_loss
        state.setdefault("history", []).append(asdict(meta))
        self._save_state(state)

        logger.info("Saved checkpoint at step=%d loss=%.4f -> %s", step, loss, ckpt_dir)
        self._prune_old_checkpoints(state)
        return meta

    def _prune_old_checkpoints(self, state: dict[str, Any]) -> None:
        """Delete checkpoint directories beyond ``save_total_limit``, keeping
        the most recent N plus whichever directory is currently `best`."""
        if self.save_total_limit <= 0:
            return

        protected = {state.get("best", {}).get("checkpoint_dir")}
        all_dirs = sorted(
            (d for d in self.root.iterdir() if d.is_dir() and d.name.startswith("checkpoint-")),
            key=lambda d: d.stat().st_mtime,
        )
        keep = set(str(d) for d in all_dirs[-self.save_total_limit :]) | protected
        for d in all_dirs:
            if str(d) not in keep and d.exists():
                shutil.rmtree(d, ignore_errors=True)
                logger.info("Pruned old checkpoint (save_total_limit=%d): %s", self.save_total_limit, d)

    def find_resume_point(self, strategy: str = "latest") -> CheckpointMeta | None:
        state = self._load_state()
        entry = state.get(strategy)
        if entry is None:
            logger.info("No checkpoint found under strategy=%s; starting fresh", strategy)
            return None
        logger.info("Resuming from %s checkpoint: step=%d", strategy, entry["step"])
        return CheckpointMeta(**entry)

    def _load_state(self) -> dict[str, Any]:
        if self.state_file.exists():
            with open(self.state_file, encoding="utf-8") as fh:
                return json.load(fh)
        return {}

    def _save_state(self, state: dict[str, Any]) -> None:
        with open(self.state_file, "w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=2)
