"""Build the RAG corpus (data/rust_corpus.jsonl) from validated pairs.

Each output line is {"content": <python-as-comment + rust solution>, "task": ...} —
the exact block format the Step 3b fine-tune saw in training, so retrieved
examples are in-distribution when prepended to the prompt. Multiple validated
solutions per task collapse to the shortest one (concise examples cost fewer
context tokens).

CLI: python -m rustgen.rag.build_corpus notebooks/pairs.jsonl data/rust_corpus.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rustgen.rag.prompt import python_as_comment


def build_corpus(pairs_path: str | Path, out_path: str | Path) -> int:
    best: dict[str, dict] = {}
    with open(pairs_path) as handle:
        for line in handle:
            if not line.strip():
                continue
            pair = json.loads(line)
            task = pair["task"]
            if task not in best or len(pair["rust_solution"]) < len(best[task]["rust_solution"]):
                best[task] = pair

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as handle:
        for pair in best.values():
            content = python_as_comment(pair["python"]) + pair["rust_solution"]
            handle.write(json.dumps({"content": content, "task": pair["task"]}) + "\n")
    return len(best)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the RAG corpus from validated pairs")
    parser.add_argument("pairs", help="pairs jsonl (task/python/rust_prompt/rust_solution)")
    parser.add_argument("out", nargs="?", default="data/rust_corpus.jsonl")
    args = parser.parse_args()
    n = build_corpus(args.pairs, args.out)
    print(f"wrote {n} example blocks to {args.out}")


if __name__ == "__main__":
    main()
