"""Overfit smoke test for LoRA trainer — 5 rows, 3 epochs."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.datasets.tend_loader import TENDLoader
from src.training.lora_trainer import train_lora
from src.utils.config import load_config


class OverfitSmokeTest(unittest.TestCase):
    """Train on 5 rows and verify loss decreases and adapter files are written."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_config()
        cls.rows = TENDLoader(config="spider").load_split("train")[:5]

    def test_overfit_smoke_text2sql(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = train_lora(
                "text2sql",
                config=self.config,
                train_rows=self.rows,
                output_dir=tmpdir,
                epochs=10,
                enable_mlflow=False,
                skip_eval=True,
            )

            adapter_config = Path(tmpdir) / "adapter_config.json"
            adapter_weights = Path(tmpdir) / "adapter_model.safetensors"
            self.assertTrue(adapter_config.is_file())
            self.assertTrue(adapter_weights.is_file())
            self.assertEqual(result.train_rows, 5)
            self.assertIsNotNone(result.train_loss)
            self.assertLess(result.train_loss, 1.5)


if __name__ == "__main__":
    unittest.main()
