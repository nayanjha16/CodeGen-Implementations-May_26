"""End-to-end pipeline orchestrator (plan §10, §11; SPEC §10 step 15).

Runs the seven stages in order, each as an **isolated subprocess** so memory is
fully released between them — this is what guarantees the teacher (Qwen-14B) never
runs concurrently with training and that Pass-1/Pass-2 student loads don't
accumulate (plan §2 memory discipline).

Stages:
    1 train    — finetune_unified.py --pass 1
    2 mine     — run_multi_task_inference.py --split train  (×3 tasks)
    3 extract  — extract_failures.py
    4 teacher  — generate_teacher_data.py   (--mock in sanity)
    5 pass2    — finetune_unified.py --pass 2 --arm control, then --arm teacher
    6 eval     — run_multi_task_inference.py --split dev  (×3 arms ×3 tasks)
    7 compare  — compare_results.py

``--sanity`` runs the whole thing on tiny slices INCLUDING BOTH Pass-2 arms and
the full eval — closing the v1 gap where sanity never exercised Pass 2 (plan §11).

Run:
    python run_codegen.py --sanity
    python run_codegen.py                      # full (overnight)
    python run_codegen.py --start_from teacher # resume from a stage
    python run_codegen.py --skip_rag           # no RAG inference variants
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys

from src import config
from src.logger import setup_logging

log = logging.getLogger(__name__)

PY = sys.executable
STAGES = ["train", "mine", "extract", "teacher", "pass2", "eval", "compare"]
ARMS = ["baseline", "control", "teacher"]


def _run(cmd: list[str]) -> None:
    """Run one subprocess stage, streaming output; abort the pipeline on failure."""
    printable = " ".join(cmd[1:])  # drop the python path for readability
    log.info("STAGE CMD: %s", printable)
    print(f"\n>>> {printable}")
    result = subprocess.run(cmd, cwd=str(config.PROJECT_ROOT))
    if result.returncode != 0:
        raise SystemExit(f"stage failed (exit {result.returncode}): {printable}")


def build_stage_commands(sanity: bool, skip_rag: bool, limit: int | None) -> dict[str, list[list[str]]]:
    """Map each stage key to the list of subprocess commands it runs."""
    s = ["--sanity"] if sanity else []
    lim = ["--limit", str(limit)] if limit is not None else []
    rag = [] if skip_rag else ["--rag"]
    rag_flag_compare = [] if skip_rag else ["--rag"]

    cmds: dict[str, list[list[str]]] = {
        "train": [[PY, "finetune_unified.py", "--pass", "1", *s, *lim]],
        "mine": [[PY, "run_multi_task_inference.py", "--task", t, "--split", "train", *rag, *s, *lim]
                 for t in config.TASKS],
        "extract": [[PY, "extract_failures.py", *s, *lim]],
        # Sanity/dev uses the deterministic mock teacher; a real run swaps in --provider local.
        "teacher": [[PY, "generate_teacher_data.py", *(["--mock"] if sanity else ["--provider", "local"]), *s, *lim]],
        "pass2": [
            [PY, "finetune_unified.py", "--pass", "2", "--arm", "control", *s, *lim],
            [PY, "finetune_unified.py", "--pass", "2", "--arm", "teacher", *s, *lim],
        ],
        "eval": [[PY, "run_multi_task_inference.py", "--task", t, "--split", "dev", "--arm", arm, *rag, *s, *lim]
                 for arm in ARMS for t in config.TASKS],
        "compare": [[PY, "compare_results.py", *rag_flag_compare]],
    }
    return cmds


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the full 7-stage codegen pipeline.")
    ap.add_argument("--start_from", choices=STAGES, default="train")
    ap.add_argument("--skip_rag", action="store_true", help="omit RAG inference variants")
    ap.add_argument("--sanity", action="store_true", help="tiny end-to-end run incl. both Pass 2 arms")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    setup_logging("run_codegen")
    cmds = build_stage_commands(args.sanity, args.skip_rag, args.limit)

    start_idx = STAGES.index(args.start_from)
    to_run = STAGES[start_idx:]
    log.info("pipeline: sanity=%s skip_rag=%s stages=%s", args.sanity, args.skip_rag, to_run)
    print(f"=== codegen pipeline: {'SANITY' if args.sanity else 'FULL'} | stages: {' -> '.join(to_run)} ===")

    for stage in to_run:
        print(f"\n===== STAGE: {stage} =====")
        log.info("===== STAGE: %s =====", stage)
        for cmd in cmds[stage]:
            _run(cmd)

    print("\n=== pipeline complete ===")
    print(f"report: {config.OUTPUTS_DIR / 'comparison_report.txt'}")
    log.info("pipeline complete")


if __name__ == "__main__":
    main()
