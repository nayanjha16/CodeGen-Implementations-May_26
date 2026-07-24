"""Tests for versioned LoRA adapter checkpoint paths."""

from __future__ import annotations

import unittest
from datetime import datetime

from src.utils.paths import (
    default_adapter_run_name,
    get_adapter_checkpoint_path,
    model_slug,
    resolve_adapter_run_name,
)


class AdapterPathTest(unittest.TestCase):
    def test_default_run_name_is_ddmm(self) -> None:
        when = datetime(2026, 6, 25, 14, 30)
        self.assertEqual(default_adapter_run_name(when), "2506")

    def test_resolve_run_name_uses_explicit_version(self) -> None:
        self.assertEqual(resolve_adapter_run_name("v1"), "v1")

    def test_adapter_checkpoint_path_includes_model_run_and_task(self) -> None:
        when = datetime(2026, 6, 25)
        model_name = "Salesforce/codegen-350M-multi"
        slug = model_slug(model_name)
        path = get_adapter_checkpoint_path(
            "nosql2doc", run="v1", model_name=model_name
        )
        self.assertTrue(
            str(path).endswith(f"models/checkpoints/{slug}/v1/nosql2doc")
        )

        default_path = get_adapter_checkpoint_path(
            "text2sql", run=None, when=when, model_name=model_name
        )
        expected_run = default_adapter_run_name(when)
        self.assertIn(
            f"models/checkpoints/{slug}/{expected_run}/text2sql",
            str(default_path),
        )


if __name__ == "__main__":
    unittest.main()
