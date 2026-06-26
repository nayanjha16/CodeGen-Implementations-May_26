"""Adapter-aware model loading tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.datasets.tend_loader import TENDLoader
from src.models.model_loader import (
    is_adapter_dir,
    load_model,
    resolve_adapter_path,
)
from src.training.filters import filter_tend_rows
from src.training.lora_trainer import train_lora
from src.training.prompt_factory import build_training_prompt
from src.training.tasks import TRAINING_TASKS
from src.utils.config import load_config


class AdapterPathTest(unittest.TestCase):
    def test_is_adapter_dir_false_for_missing_path(self) -> None:
        self.assertFalse(is_adapter_dir(Path("/tmp/nonexistent_adapter_dir")))

    def test_resolve_adapter_path_from_explicit_dir(self) -> None:
        config = load_config()
        rows = TENDLoader(config="spider").load_split("train")[:3]
        with tempfile.TemporaryDirectory() as tmpdir:
            train_lora(
                "text2sql",
                config=config,
                train_rows=rows,
                output_dir=tmpdir,
                epochs=3,
                skip_eval=True,
                enable_mlflow=False,
            )
            self.assertTrue(is_adapter_dir(tmpdir))
            resolved = resolve_adapter_path(adapter_path=tmpdir, config=config)
            self.assertEqual(resolved, Path(tmpdir))


class AdapterLoadTest(unittest.TestCase):
    """Train tiny adapters and verify load_model + generate for each task."""

    _tmpdir: tempfile.TemporaryDirectory
    adapter_dirs: dict[str, Path]
    rows: list[dict[str, str]]
    config: dict

    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_config()
        cls.rows = TENDLoader(config="spider").load_split("train")
        cls._tmpdir = tempfile.TemporaryDirectory()
        cls.adapter_dirs = {}
        base = Path(cls._tmpdir.name)

        for task in sorted(TRAINING_TASKS):
            kept = filter_tend_rows(cls.rows, task)[:3]
            out = base / task
            train_lora(
                task,
                config=cls.config,
                train_rows=kept,
                output_dir=out,
                epochs=5,
                skip_eval=True,
                enable_mlflow=False,
            )
            cls.adapter_dirs[task] = out

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmpdir.cleanup()

    def test_load_and_generate_for_each_task(self) -> None:
        sample = self.rows[0]
        for task in sorted(TRAINING_TASKS):
            adapter_dir = self.adapter_dirs[task]
            model = load_model(
                config=self.config,
                adapter_path=adapter_dir,
                eager=True,
            )
            self.assertEqual(model.adapter_path, adapter_dir)
            prompt = build_training_prompt(sample, task, config=self.config)
            output = model.generate(prompt, max_new_tokens=32, decoding_strategy="greedy")
            self.assertIsInstance(output, str)
            self.assertGreater(len(output.strip()), 0, msg=f"empty generation for {task}")

    def test_load_model_without_adapter_unchanged(self) -> None:
        model = load_model(config=self.config, eager=True)
        self.assertIsNone(model.adapter_path)
        prompt = build_training_prompt(self.rows[0], "text2sql", config=self.config)
        output = model.generate(prompt, max_new_tokens=16, decoding_strategy="greedy")
        self.assertIsInstance(output, str)


if __name__ == "__main__":
    unittest.main()
