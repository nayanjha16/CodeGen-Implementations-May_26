"""Prompt parity and dataset filter tests for LoRA SFT builder."""

from __future__ import annotations

import unittest

from src.datasets.tend_loader import TENDLoader
from src.text2sql.sql_executor import (
    build_documentation_prompt,
    build_nosql_prompt,
    build_text2sql_prompt,
)
from src.training.filters import FilterStats, filter_tend_rows
from src.training.prompt_factory import build_training_prompt, build_training_target
from src.training.tasks import TRAINING_TASKS
from src.training.tend_dataset import build_sft_examples, load_tend_training_rows
from src.utils.config import load_config


class PromptParityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_config()
        cls.rows = TENDLoader(config="spider").load_split("train")[:3]

    def test_text2sql_prompt_matches_runtime_builder(self) -> None:
        for row in self.rows:
            expected = build_text2sql_prompt(
                row["question"],
                row["schema"],
                config=self.config,
            )
            actual = build_training_prompt(row, "text2sql", config=self.config)
            self.assertEqual(actual, expected)

    def test_sql2nosql_prompt_matches_runtime_builder(self) -> None:
        for row in self.rows:
            expected = build_nosql_prompt(
                row["sql"],
                row["schema"],
                nosql_schema=row["nosql_schema"],
                config=self.config,
            )
            actual = build_training_prompt(row, "sql2nosql", config=self.config)
            self.assertEqual(actual, expected)

    def test_nosql2doc_prompt_matches_runtime_builder(self) -> None:
        for row in self.rows:
            expected = build_documentation_prompt(
                row["nosql_query"],
                row["schema"],
                nosql_schema=row["nosql_schema"],
                question=row["question"],
                config=self.config,
            )
            actual = build_training_prompt(row, "nosql2doc", config=self.config)
            self.assertEqual(actual, expected)


class DatasetFilterTest(unittest.TestCase):
    def test_filter_keeps_complete_rows(self) -> None:
        rows = load_tend_training_rows()[:20]
        stats = FilterStats()
        for task in sorted(TRAINING_TASKS):
            kept = filter_tend_rows(rows, task, stats=stats)
            self.assertGreater(len(kept), 0, msg=f"no rows kept for {task}")

    def test_build_examples_include_text_column(self) -> None:
        rows = TENDLoader(config="spider").load_split("train")[:5]
        examples, stats, token_stats = build_sft_examples(
            rows,
            "text2sql",
            config=load_config(),
            max_samples=5,
        )
        self.assertGreater(len(examples), 0)
        self.assertTrue(all("text" in example for example in examples))
        self.assertTrue(all(example["text"].endswith(example["target"]) for example in examples))
        self.assertEqual(
            examples[0]["target"],
            build_training_target(rows[0], "text2sql"),
        )

    def test_prompt_respects_max_length_budget(self) -> None:
        from src.models.model_loader import load_tokenizer
        from src.utils.config import get_training_config

        config = load_config()
        training_cfg = get_training_config(config)
        max_length = int(training_cfg["max_length"])
        tokenizer = load_tokenizer(config=config)

        rows = TENDLoader(config="spider").load_split("train")[:50]
        examples, _, _ = build_sft_examples(
            rows,
            "nosql2doc",
            config=config,
            tokenizer=tokenizer,
            max_samples=50,
        )
        self.assertGreater(len(examples), 0)
        for example in examples:
            prompt_tokens = len(
                tokenizer.encode(example["prompt"], add_special_tokens=False)
            )
            target_tokens = len(
                tokenizer.encode(example["target"], add_special_tokens=False)
            )
            self.assertLessEqual(
                prompt_tokens + target_tokens,
                max_length - 1,
                msg="prompt+target must leave room for TRL's appended EOS",
            )


if __name__ == "__main__":
    unittest.main()
