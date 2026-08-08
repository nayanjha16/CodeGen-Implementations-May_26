"""Multi-task inference — failure mining (train) and evaluation (dev) (plan §8, §9).

Same script, two jobs distinguished by ``--split`` (load-bearing, SPEC §7):
- ``--split train`` → **failure mining**: run the Pass-1 model over the TRAIN split
  (draft-only) to find where it is still wrong. Output feeds ``extract_failures.py``.
- ``--split dev``  → **evaluation**: score an arm's checkpoint on the untouched dev
  split. Two-stage (draft→revise) for arms B/C; draft-only for arm A (baseline).

**Arm A is draft-only, arms B/C are two-stage** (SPEC §6.4): a baseline checkpoint
never learned to revise, so it is scored on its Stage-A draft; control/teacher get
the full draft→revise pass. RAG references are self-excluded by uid — load-bearing
on the train split so a query never retrieves its own gold (SPEC-REVIEW #5).

Run:
    python run_multi_task_inference.py --task text2sql --split dev --arm baseline
    python run_multi_task_inference.py --task sql2nosql --split train --rag
"""

from __future__ import annotations

import argparse
import json
import logging

from src import config, loader, splits
from src import model_factory as mf
from src import mongo_exec, sql_exec
from src.device import describe, enable_mps_cpu_fallback
from src.generator import generate_and_extract
from src.logger import setup_logging
from src.prompt_builder import build_prompt, input_value
from src.retriever import get_retriever

log = logging.getLogger(__name__)

# Arm → (checkpoint dir, is two-stage). Baseline = Pass 1, draft-only.
ARMS = {
    "baseline": (config.PASS1_DIR, False),
    "control": (config.PASS2_CONTROL_DIR, True),
    "teacher": (config.PASS2_TEACHER_DIR, True),
}


def _is_correct(task: str, ex, prediction: str) -> bool:
    """Execution-based correctness (never string match) — SQL via sqlite, NoSQL via mongosh."""
    if task == "text2sql":
        return sql_exec.is_correct(ex.db_id, ex.gold, prediction)
    order_sensitive = mongo_exec.implies_order(gold_sql=ex.aux_sql, gold_mql=ex.gold)
    return mongo_exec.is_correct(ex.db_id, ex.gold, prediction, order_sensitive)


def load_examples(task: str, split: str, limit: int | None):
    """Train partition (mining) or dev set (eval) for one task."""
    if split == "train":
        exs = loader.load_task(task, "train")
        name = "spider" if task == "text2sql" else task
        exs, _valid = splits.carve_valid(exs, name)
    else:
        exs = loader.load_task(task, "dev")
    return exs[:limit] if limit is not None else exs


def _output_path(split: str, arm: str, task: str, rag: bool):
    if split == "train":
        d = config.OUTPUTS_DIR / "codegen" / "pass1_train" / task
        fname = "predictions.json"
    else:
        d = config.OUTPUTS_DIR / "codegen" / "eval" / arm / task
        fname = "predictions_rag.json" if rag else "predictions.json"
    d.mkdir(parents=True, exist_ok=True)
    return d / fname


def run(task: str, split: str, arm: str, rag: bool, two_stage: bool,
        limit: int | None, batch_size: int) -> dict:
    enable_mps_cpu_fallback()
    log.info("startup: %s", describe())
    ckpt, _ = ARMS[arm]
    if not ckpt.exists():
        raise FileNotFoundError(f"checkpoint for arm {arm!r} missing: {ckpt}")

    tokenizer = mf.load_tokenizer()
    model = mf.load_adapter(ckpt, trainable=False)
    retriever = get_retriever(task) if rag else None

    examples = load_examples(task, split, limit)
    log.info("inference: task=%s split=%s arm=%s rag=%s two_stage=%s n=%d",
             task, split, arm, rag, two_stage, len(examples))

    records = []
    n_correct = 0
    for start in range(0, len(examples), batch_size):
        batch = examples[start:start + batch_size]

        # Stage A — draft (with self-excluded RAG reference if enabled).
        refs = [None] * len(batch)
        if retriever is not None:
            refs = [(_r[0] if (_r := retriever.retrieve_for(e, top_k=1)) else None) for e in batch]
        prompts_a = [build_prompt(e, reference=r) for e, r in zip(batch, refs)]
        drafts = [q for _a, q in generate_and_extract(model, tokenizer, prompts_a, task)]

        if two_stage:
            # Stage B — revise, conditioned on the model's own draft.
            prompts_b = [build_prompt(e, reference=r, broken_draft=d)
                         for e, r, d in zip(batch, refs, drafts)]
            revised = generate_and_extract(model, tokenizer, prompts_b, task)
            analyses = [a for a, _q in revised]
            preds = [q for _a, q in revised]
        else:
            analyses = [None] * len(batch)
            preds = drafts

        for e, draft, analysis, pred in zip(batch, drafts, analyses, preds):
            rec = {
                "db_id": e.db_id, "task": task, "difficulty": e.difficulty,
                "question": e.question, "source_sql": e.source_sql,
                "aux_sql": e.aux_sql,  # gold SQL, for NoSQL ORDER BY detection downstream
                "gold": e.gold, "prediction": pred, "draft": draft,
            }
            if two_stage:
                rec["analysis"] = analysis
            if split == "dev":  # eval schema carries execution correctness (SPEC §6.2)
                rec["correct"] = _is_correct(task, e, pred)
                n_correct += int(rec["correct"])
            records.append(rec)
        log.info("  processed %d/%d", min(start + batch_size, len(examples)), len(examples))

    out_path = _output_path(split, arm, task, rag)
    out_path.write_text(json.dumps(records, indent=1), encoding="utf-8")

    summary = {"task": task, "split": split, "arm": arm, "n": len(records), "path": str(out_path)}
    if split == "dev":
        summary["accuracy"] = round(n_correct / max(len(records), 1), 4)
        summary["n_correct"] = n_correct
    log.info("wrote %s", summary)
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description="Multi-task inference (mining / evaluation).")
    ap.add_argument("--task", choices=config.TASKS, required=True)
    ap.add_argument("--split", choices=("train", "dev"), required=True)
    ap.add_argument("--arm", choices=tuple(ARMS), default="baseline")
    ap.add_argument("--rag", action="store_true", help="use retrieved references")
    ap.add_argument("--two_stage", dest="two_stage", action="store_true", default=None)
    ap.add_argument("--draft_only", dest="two_stage", action="store_false")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--sanity", action="store_true")
    ap.add_argument("--batch_size", type=int, default=8)
    args = ap.parse_args()

    setup_logging(f"infer_{args.task}_{args.split}_{args.arm}")
    limit = 6 if args.sanity and args.limit is None else args.limit
    # Default staging: arm A draft-only, arms B/C two-stage. Mining is always draft-only.
    two_stage = args.two_stage
    if two_stage is None:
        two_stage = ARMS[args.arm][1] and args.split == "dev"
    summary = run(args.task, args.split, args.arm, args.rag, two_stage, limit, args.batch_size)
    print(summary)


if __name__ == "__main__":
    main()
