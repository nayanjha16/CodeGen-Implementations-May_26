"""Tests for versioned LoRA adapter checkpoint paths."""

from __future__ import annotations

import unittest
from datetime import datetime

from src.utils.paths import (
    default_adapter_run_name,
    get_adapter_checkpoint_path,
    resolve_adapter_run_name,
)


class AdapterPathTest(unittest.TestCase):
    def test_default_run_name_is_ddmm(self) -> None:
        when = datetime(2026, 6, 25, 14, 30)
        self.assertEqual(default_adapter_run_name(when), "2506")

    def test_resolve_run_name_uses_explicit_version(self) -> None:
        self.assertEqual(resolve_adapter_run_name("v1"), "v1")

    def test_adapter_checkpoint_path_includes_run_and_task(self) -> None:
        when = datetime(2026, 6, 25)
        path = get_adapter_checkpoint_path("nosql2doc", run="v1")
        self.assertTrue(str(path).endswith("models/checkpoints/v1/nosql2doc"))

        default_path = get_adapter_checkpoint_path("text2sql", run=None)
        expected_run = default_adapter_run_name(when)
        self.assertIn(f"models/checkpoints/{expected_run}/text2sql", str(default_path))


if __name__ == "__main__":
    unittest.main()
