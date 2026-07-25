"""Build the RAG corpus from validated pairs.

Two styles, one per subject model:

- ``translation`` (the 350M-era default): content = python-as-comment + rust
  solution — the exact block format the Step 3b fine-tune saw in training.
- ``completion`` (the Qwen/Step 6 format): content = the pure-Rust solution
  (`///` doc + fn), plus a ``retrieval_text`` field holding the pair's doc
  comment + signature so retrieval matches on the same information the query
  has (the Step 6 sweep retrieved by Rust-prompt similarity, not Python).

Multiple validated solutions per task collapse to the shortest one (concise
examples cost fewer context tokens).

CLI: python -m rustgen.rag.build_corpus --style completion notebooks/pairs.jsonl data/rust_corpus_qwen.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rustgen.rag.prompt import python_as_comment


def build_corpus(pairs_path: str | Path, out_path: str | Path,
                 style: str = "translation") -> int:
    if style not in ("translation", "completion"):
        raise ValueError(f"unknown corpus style: {style!r}")
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
            if style == "translation":
                doc = {"content": python_as_comment(pair["python"]) + pair["rust_solution"],
                       "task": pair["task"]}
            else:
                doc = {"content": pair["rust_solution"].rstrip(),
                       "retrieval_text": pair["rust_prompt"],
                       "task": pair["task"]}
            handle.write(json.dumps(doc) + "\n")
    return len(best)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the RAG corpus from validated pairs")
    parser.add_argument("pairs", help="pairs jsonl (task/python/rust_prompt/rust_solution)")
    parser.add_argument("out", nargs="?", default="data/rust_corpus_qwen.jsonl")
    parser.add_argument("--style", choices=("translation", "completion"),
                        default="completion",
                        help="translation = 350M/Step 3b block format; "
                             "completion = pure-Rust Qwen/Step 6 format (default)")
    args = parser.parse_args()
    n = build_corpus(args.pairs, args.out, style=args.style)
    print(f"wrote {n} {args.style}-style example blocks to {args.out}")


if __name__ == "__main__":
    main()
