"""Smoke test for LoRA trainer — 1 row, 1 epoch."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.datasets.tend_loader import TENDLoader
from src.training.lora_trainer import train_lora
from src.utils.config import load_config
from src.utils.logging import log_step


class OverfitSmokeTest(unittest.TestCase):
    """Train on 1 row for 1 epoch and verify adapter files are written."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_config()
        cls.rows = TENDLoader(config="spider").load_split("train")[:1]

    def test_overfit_smoke_text2sql(self) -> None:
        log_step("text2sql", "Smoke test: 1 row, 1 epoch")
        with tempfile.TemporaryDirectory() as tmpdir:
            result = train_lora(
                "text2sql",
                config=self.config,
                train_rows=self.rows,
                output_dir=tmpdir,
                epochs=1,
                enable_mlflow=False,
                skip_eval=True,
            )

            adapter_config = Path(tmpdir) / "adapter_config.json"
            adapter_weights = Path(tmpdir) / "adapter_model.safetensors"
            self.assertTrue(adapter_config.is_file())
            self.assertTrue(adapter_weights.is_file())
            self.assertEqual(result.train_rows, 1)
            self.assertIsNotNone(result.train_loss)


if __name__ == "__main__":
    unittest.main()
