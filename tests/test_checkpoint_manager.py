from __future__ import annotations

import time
from pathlib import Path

from codegen_rag.training.checkpoint_manager import CheckpointManager


class FakeModel:
    """Stands in for a HF/PEFT model — just needs save_pretrained(dir)."""

    def save_pretrained(self, path: Path) -> None:
        Path(path).mkdir(parents=True, exist_ok=True)
        (Path(path) / "adapter_model.bin").write_bytes(b"fake-weights")


def test_save_creates_checkpoint_dir(tmp_path: Path):
    manager = CheckpointManager(tmp_path)
    meta = manager.save(FakeModel(), step=10, epoch=0, loss=1.5)
    assert Path(meta.checkpoint_dir).exists()
    assert (Path(meta.checkpoint_dir) / "adapter_model.bin").exists()


def test_find_resume_point_returns_none_when_empty(tmp_path: Path):
    manager = CheckpointManager(tmp_path)
    assert manager.find_resume_point("latest") is None


def test_find_resume_point_returns_latest_after_save(tmp_path: Path):
    manager = CheckpointManager(tmp_path)
    manager.save(FakeModel(), step=10, epoch=0, loss=1.5)
    manager.save(FakeModel(), step=20, epoch=0, loss=1.2)
    resumed = manager.find_resume_point("latest")
    assert resumed.step == 20


def test_best_checkpoint_tracks_lowest_loss(tmp_path: Path):
    manager = CheckpointManager(tmp_path)
    manager.save(FakeModel(), step=10, epoch=0, loss=2.0)
    manager.save(FakeModel(), step=20, epoch=0, loss=0.5)  # new best
    manager.save(FakeModel(), step=30, epoch=0, loss=1.8)  # worse than best
    best = manager.find_resume_point("best")
    assert best.step == 20
    assert best.loss == 0.5


def test_save_total_limit_prunes_old_checkpoints(tmp_path: Path):
    manager = CheckpointManager(tmp_path, save_total_limit=2)
    for step in range(1, 6):
        manager.save(FakeModel(), step=step * 10, epoch=0, loss=1.0)
        time.sleep(0.01)  # ensure distinct mtimes for deterministic ordering

    remaining = sorted(d.name for d in tmp_path.iterdir() if d.is_dir())
    # Only the 2 most recent checkpoints should remain (best_loss ties on
    # first save, so no extra "best" directory is protected here).
    assert len(remaining) <= 3  # allow for the protected "best" if distinct
    assert "checkpoint-000050" in remaining  # most recent must survive


def test_save_total_limit_always_protects_best(tmp_path: Path):
    manager = CheckpointManager(tmp_path, save_total_limit=1)
    manager.save(FakeModel(), step=10, epoch=0, loss=0.1)  # best, will get pruned candidate later
    for step in range(2, 6):
        manager.save(FakeModel(), step=step * 10, epoch=0, loss=5.0)  # much worse
        time.sleep(0.01)

    remaining = {d.name for d in tmp_path.iterdir() if d.is_dir()}
    assert "checkpoint-000010" in remaining  # best must survive despite being oldest


def test_save_total_limit_zero_disables_pruning(tmp_path: Path):
    manager = CheckpointManager(tmp_path, save_total_limit=0)
    for step in range(1, 4):
        manager.save(FakeModel(), step=step * 10, epoch=0, loss=1.0)
    remaining = [d for d in tmp_path.iterdir() if d.is_dir()]
    assert len(remaining) == 3
