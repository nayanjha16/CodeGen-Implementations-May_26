"""Run a Translator over humaneval-rs-style problems and report pass@1.

CLI: python -m rustgen.eval.runner --limit 10 [--dataset path.jsonl] [--rag]
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path

from rustgen.config import Config
from rustgen.eval.harness import run_rust
from rustgen.rag import get_retriever
from rustgen.rag.retriever import Retriever
from rustgen.translator import get_translator
from rustgen.translator.base import TranslationTask, Translator

DEFAULT_DATASET = (
    Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "humaneval_rs_sample.jsonl"
)


@dataclass
class EvalReport:
    total: int = 0
    passed: int = 0
    results: list[dict] = field(default_factory=list)

    @property
    def pass_at_1(self) -> float:
        return self.passed / self.total if self.total else 0.0

    def summary(self) -> dict:
        return {"total": self.total, "passed": self.passed, "pass@1": round(self.pass_at_1, 4)}


def evaluate(
    translator: Translator,
    dataset_path: str | Path,
    limit: int | None = None,
    retriever: Retriever | None = None,
    rag_k: int = 3,
) -> EvalReport:
    """Iterate jsonl problems ({"task_id", "prompt", "tests"}), generate, harness-test."""
    with open(dataset_path) as handle:
        problems = [json.loads(line) for line in handle if line.strip()]
    if limit is not None:
        problems = problems[:limit]

    report = EvalReport()
    for problem in problems:
        task = TranslationTask(description=problem["prompt"])
        if retriever is not None:
            task.context_examples = retriever.retrieve(task.description, rag_k)
        code = translator.generate(task)
        result = run_rust(code, problem["tests"])
        report.total += 1
        report.passed += int(result.passed)
        report.results.append(
            {"task_id": problem["task_id"], "passed": result.passed, "stage": result.stage}
        )
        status = "PASS" if result.passed else f"FAIL ({result.stage})"
        print(f"[{report.total}/{len(problems)}] {problem['task_id']}: {status}"
              f"  running pass@1 = {report.pass_at_1:.2%}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a translator on humaneval-rs")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET),
                        help="jsonl with task_id/prompt/tests per line")
    parser.add_argument("--limit", type=int, default=None, help="evaluate first N problems")
    parser.add_argument("--rag", action="store_true", help="force RAG on")
    args = parser.parse_args()

    config = Config.from_env()
    if args.rag:
        config.rag_enabled = True
    translator = get_translator(config)
    retriever = get_retriever(config) if config.rag_enabled else None

    print(f"backend={config.backend}  rag={'on' if retriever else 'off'}  dataset={args.dataset}")
    report = evaluate(translator, args.dataset, args.limit, retriever, config.rag_k)
    print(json.dumps(report.summary()))


if __name__ == "__main__":
    main()
