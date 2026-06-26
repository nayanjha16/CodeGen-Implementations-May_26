"""Tests for LoRA adapter artifact verification."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.datasets.tend_loader import TENDLoader
from src.training.adapter_verify import verify_adapter_dir, verify_all_adapters
from src.training.lora_trainer import train_lora
from src.utils.config import load_config


class AdapterVerifyTest(unittest.TestCase):
    def test_verify_adapter_dir_after_training(self) -> None:
        config = load_config()
        rows = TENDLoader(config="spider").load_split("train")[:3]
        with tempfile.TemporaryDirectory() as tmpdir:
            train_lora(
                "text2sql",
                config=config,
                train_rows=rows,
                output_dir=tmpdir,
                epochs=2,
                skip_eval=True,
                enable_mlflow=False,
            )
            result = verify_adapter_dir("text2sql", adapter_path=tmpdir, config=config)
            self.assertTrue(result.ok)
            self.assertIsNotNone(result.metadata)

    def test_verify_all_adapters_missing_dirs(self) -> None:
        config = load_config()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Point checkpoints to empty temp dir via env override in verify with explicit paths
            rows = TENDLoader(config="spider").load_split("train")[:2]
            base = Path(tmpdir)
            for task in ("text2sql", "sql2nosql", "nosql2doc"):
                out = base / task
                train_lora(
                    task,
                    config=config,
                    train_rows=rows,
                    output_dir=out,
                    epochs=2,
                    skip_eval=True,
                    enable_mlflow=False,
                )
            results = {
                task: verify_adapter_dir(task, adapter_path=base / task, config=config)
                for task in ("text2sql", "sql2nosql", "nosql2doc")
            }
            self.assertTrue(all(res.ok for res in results.values()))


if __name__ == "__main__":
    unittest.main()
