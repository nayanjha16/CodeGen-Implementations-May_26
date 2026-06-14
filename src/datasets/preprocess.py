"""Dataset preprocessing, cleaning, and statistics."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


def clean_sql(sql: str) -> str:
    """Normalize SQL whitespace and strip trailing semicolons."""
    sql = sql.strip()
    sql = re.sub(r"\s+", " ", sql)
    if sql.endswith(";"):
        sql = sql[:-1].strip()
    return sql


def clean_question(question: str) -> str:
    """Normalize natural language questions."""
    question = question.strip()
    question = re.sub(r"\s+", " ", question)
    return question


class DatasetPreprocessor:
    """Clean and split datasets into standardized format."""

    def __init__(self, output_dir: str | Path = "data/processed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def clean_examples(self, examples: list[dict[str, str]]) -> list[dict[str, str]]:
        """Apply cleaning to all examples."""
        cleaned = []
        for ex in examples:
            cleaned.append(
                {
                    "question": clean_question(ex.get("question", "")),
                    "schema": ex.get("schema", "").strip(),
                    "sql": clean_sql(ex.get("sql", "")),
                    **{k: v for k, v in ex.items() if k not in ("question", "schema", "sql")},
                }
            )
        return [ex for ex in cleaned if ex["question"] and ex["sql"]]

    def train_test_split(
        self,
        examples: list[dict[str, str]],
        test_ratio: float = 0.1,
        seed: int = 42,
    ) -> tuple[list[dict], list[dict]]:
        """Split examples into train and test sets."""
        import random

        rng = random.Random(seed)
        shuffled = examples.copy()
        rng.shuffle(shuffled)
        split_idx = int(len(shuffled) * (1 - test_ratio))
        return shuffled[:split_idx], shuffled[split_idx:]

    def save(self, examples: list[dict], name: str) -> Path:
        """Save processed examples to JSON."""
        out_path = self.output_dir / f"{name}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(examples, f, indent=2, ensure_ascii=False)
        return out_path

    def process_and_save(
        self,
        examples: list[dict[str, str]],
        name: str,
    ) -> dict[str, Any]:
        """Clean, compute stats, and save dataset."""
        cleaned = self.clean_examples(examples)
        stats = compute_statistics(cleaned)
        path = self.save(cleaned, name)
        return {"path": str(path), "count": len(cleaned), "statistics": stats}


def compute_statistics(examples: list[dict[str, str]]) -> dict[str, Any]:
    """Compute dataset statistics for research reporting."""
    if not examples:
        return {"count": 0}

    question_lengths = [len(ex["question"].split()) for ex in examples]
    sql_lengths = [len(ex["sql"].split()) for ex in examples]
    sql_keywords = Counter()

    keywords = ["SELECT", "WHERE", "JOIN", "GROUP", "ORDER", "HAVING", "LIMIT"]
    for ex in examples:
        sql_upper = ex["sql"].upper()
        for kw in keywords:
            if kw in sql_upper:
                sql_keywords[kw] += 1

    return {
        "count": len(examples),
        "avg_question_length": sum(question_lengths) / len(question_lengths),
        "avg_sql_length": sum(sql_lengths) / len(sql_lengths),
        "max_question_length": max(question_lengths),
        "max_sql_length": max(sql_lengths),
        "sql_keyword_distribution": dict(sql_keywords),
        "unique_schemas": len({ex.get("schema", "") for ex in examples}),
    }
