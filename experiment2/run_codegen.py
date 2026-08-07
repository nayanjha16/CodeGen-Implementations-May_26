"""
CodeGen end-to-end pipeline orchestrator.

Stages (in order):
  1.  Pass 1 fine-tune      — finetune_unified.py
  2.  Pass 1 inference      — run_multi_task_inference.py  (all 3 tasks, no RAG)
  3.  Extract failures      — extract_failures.py
  4.  Teacher annotation    — generate_teacher_data.py
  5.  Pass 2 fine-tune      — finetune_unified.py  (augmented data)
  6.  Pass 2 inference      — run_multi_task_inference.py  (all 3 tasks, no RAG + RAG)
  7.  Compare results       — compare_results.py

Usage:
    python run_codegen.py                         # full pipeline
    python run_codegen.py --start_from inference  # skip Pass 1 training
    python run_codegen.py --start_from teacher    # skip to teacher step
    python run_codegen.py --start_from pass2      # skip to Pass 2 fine-tune
    python run_codegen.py --start_from pass2_infer  # skip to Pass 2 inference
    python run_codegen.py --skip_rag              # skip RAG inference runs
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime

from src.config import MODELS, DATA
from src.logger import pipeline_logger

cfg = MODELS["codegen"]

# Convenience path constants pulled from config
CKPT_P1          = cfg["checkpoint_pass1"]
CKPT_P2          = cfg["checkpoint_pass2"]

OUT_TEXT2SQL_P1  = cfg["output_text2sql"]
OUT_SQL2NOSQL_P1 = cfg["output_sql2nosql"]
OUT_TEXT2NOSQL_P1= cfg["output_text2nosql"]

OUT_TEXT2SQL_P2  = cfg["output_text2sql_p2"]
OUT_SQL2NOSQL_P2 = cfg["output_sql2nosql_p2"]
OUT_TEXT2NOSQL_P2= cfg["output_text2nosql_p2"]

SPIDER_AUG       = DATA["spider_augmented_train"]
DOCSPIDER_AUG    = DATA["docspider_augmented_train"]

# Failure prediction paths — output dirs of Pass 1 inference
P1_TEXT2SQL_PRED  = os.path.join(OUT_TEXT2SQL_P1,  "predictions.json")
P1_SQL2NOSQL_PRED = os.path.join(OUT_SQL2NOSQL_P1, "predictions.json")
P1_TEXT2NOSQL_PRED= os.path.join(OUT_TEXT2NOSQL_P1,"predictions.json")

BAR = "=" * 72


# ---------------------------------------------------------------------------
# Subprocess runner
# ---------------------------------------------------------------------------

def _run(label: str, *cmd_args):
    cmd = [sys.executable] + list(cmd_args)
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"\n{BAR}")
    print(f"  [{ts}] {label}")
    print(f"{BAR}\n")
    pipeline_logger.info("orchestration", "step_start", stats={"label": label, "cmd": " ".join(cmd_args)})

    result = subprocess.run(cmd)
    ts_end = datetime.now().strftime("%H:%M:%S")

    if result.returncode != 0:
        pipeline_logger.error("orchestration", "step_failed",
                              stats={"label": label, "exit_code": result.returncode, "end_time": ts_end})
        print(f"\n[run_codegen] ERROR in '{label}' (exit {result.returncode}). Stopping.")
        sys.exit(result.returncode)

    pipeline_logger.info("orchestration", "step_complete",
                         stats={"label": label, "exit_code": 0, "end_time": ts_end})


# ---------------------------------------------------------------------------
# Stage definitions
# ---------------------------------------------------------------------------

def stage_pass1_train(limit=None):
    extra = ["--limit", str(limit)] if limit else []
    _run(
        "Pass 1 — Fine-tune CodeGen (standard multi-task)",
        "finetune_unified.py",
        "--checkpoint_dir", CKPT_P1,
        *extra,
    )


def stage_pass1_inference(limit=None):
    extra = ["--limit", str(limit)] if limit else []
    for task, out_dir in [
        ("text2sql",  OUT_TEXT2SQL_P1),
        ("sql2nosql", OUT_SQL2NOSQL_P1),
        ("text2nosql",OUT_TEXT2NOSQL_P1),
    ]:
        _run(
            f"Pass 1 Inference — {task}",
            "run_multi_task_inference.py",
            "--task",              task,
            "--checkpoint_override", CKPT_P1,
            "--output_dir",        out_dir,
            *extra,
        )
        _run(
            f"Pass 1 Inference +RAG — {task}",
            "run_multi_task_inference.py",
            "--task",              task,
            "--rag",
            "--checkpoint_override", CKPT_P1,
            "--output_dir",        out_dir,
            *extra,
        )


def stage_extract_failures():
    _run(
        "Extract Pass 1 failures",
        "extract_failures.py",
        "--text2sql_pred",   P1_TEXT2SQL_PRED,
        "--sql2nosql_pred",  P1_SQL2NOSQL_PRED,
        "--text2nosql_pred", P1_TEXT2NOSQL_PRED,
    )


def stage_teacher(mock=False):
    extra = ["--mock_teacher"] if mock else []
    _run(
        "Teacher LLM inference — generate Pass 2 calibration data" + (" (MOCK)" if mock else ""),
        "generate_teacher_data.py",
        *extra,
    )


def stage_pass2_train(limit=None):
    extra = ["--limit", str(limit)] if limit else []
    _run(
        "Pass 2 — Fine-tune CodeGen (teacher-calibrated data, starting from Pass 1 weights)",
        "finetune_unified.py",
        "--spider_data",    SPIDER_AUG,
        "--docspider_data", DOCSPIDER_AUG,
        "--checkpoint_dir", CKPT_P2,
        "--resume_from",    CKPT_P1,
        *extra,
    )


def stage_ensure_retrieval_index():
    """Build the retrieval index if any required file is missing."""
    tasks = ["text2sql", "sql2nosql", "text2nosql"]
    missing = [
        t for t in tasks
        if not os.path.exists(os.path.join("retrieval_index", f"{t}_embeddings.npy"))
        or not os.path.exists(os.path.join("retrieval_index", f"{t}_metadata.json"))
    ]

    if not missing:
        pipeline_logger.info("orchestration", "retrieval_index_exists", stats={"tasks": tasks})
        print("[run_codegen] Retrieval index present for all tasks — skipping build.")
        return

    pipeline_logger.info("orchestration", "retrieval_index_missing", stats={"missing_tasks": missing})
    print(f"[run_codegen] Retrieval index missing for: {missing}. Building now...")
    _run(
        "Build retrieval index (BM25 + dense embeddings)",
        os.path.join("scripts", "build_retrieval_index.py"),
    )


def stage_pass2_inference(run_rag: bool, limit=None):
    if run_rag:
        stage_ensure_retrieval_index()

    extra = ["--limit", str(limit)] if limit else []
    for task, out_dir in [
        ("text2sql",  OUT_TEXT2SQL_P2),
        ("sql2nosql", OUT_SQL2NOSQL_P2),
        ("text2nosql",OUT_TEXT2NOSQL_P2),
    ]:
        _run(
            f"Pass 2 Inference — {task}",
            "run_multi_task_inference.py",
            "--task",              task,
            "--checkpoint_override", CKPT_P2,
            "--output_dir",        out_dir,
            *extra,
        )
        if run_rag:
            _run(
                f"Pass 2 Inference +RAG — {task}",
                "run_multi_task_inference.py",
                "--task",              task,
                "--rag",
                "--checkpoint_override", CKPT_P2,
                "--output_dir",        out_dir,
                *extra,
            )


def stage_compare():
    _run("Generate cross-model comparison report", "compare_results.py")


# ---------------------------------------------------------------------------
# Stage ordering map — used by --start_from
# ---------------------------------------------------------------------------

STAGE_ORDER = [
    "train",
    "inference",
    "extract",
    "teacher",
    "pass2",
    "pass2_infer",
    "compare",
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="CodeGen end-to-end pipeline runner")
    parser.add_argument(
        "--start_from",
        choices=STAGE_ORDER,
        default="train",
        help=(
            "Resume from a specific stage, skipping all earlier ones. "
            "Choices: train | inference | extract | teacher | pass2 | pass2_infer | compare"
        ),
    )
    parser.add_argument(
        "--skip_rag",
        action="store_true",
        help="Skip the RAG inference runs in Pass 2 (saves time on CPU).",
    )
    parser.add_argument(
        "--sanity",
        action="store_true",
        help="Sanity-test mode: run all stages on 3 samples only, with teacher mocked (no API call needed).",
    )
    args = parser.parse_args()

    start_idx = STAGE_ORDER.index(args.start_from)
    run_rag   = not args.skip_rag
    limit     = 3 if args.sanity else None
    mock      = args.sanity

    pipeline_logger.info("orchestration", "pipeline_start", stats={
        "start_from":   args.start_from,
        "run_rag":      run_rag,
        "sanity":       args.sanity,
        "ckpt_pass1":   CKPT_P1,
        "ckpt_pass2":   CKPT_P2,
    })
    print(f"\n{'='*72}")
    print(f"  CodeGen Pipeline  |  starting from: {args.start_from.upper()}"
          + ("  [SANITY MODE — 3 samples]" if args.sanity else ""))
    print(f"{'='*72}")

    if start_idx <= STAGE_ORDER.index("train"):
        stage_ensure_retrieval_index()   # needed for semantic RAG during training
        stage_pass1_train(limit=limit)

    if start_idx <= STAGE_ORDER.index("inference"):
        stage_ensure_retrieval_index()   # idempotent — skips if already built
        stage_pass1_inference(limit=limit)

    if start_idx <= STAGE_ORDER.index("extract"):
        stage_extract_failures()

    if start_idx <= STAGE_ORDER.index("teacher"):
        stage_teacher(mock=mock)

    if start_idx <= STAGE_ORDER.index("pass2"):
        stage_pass2_train(limit=limit)

    if start_idx <= STAGE_ORDER.index("pass2_infer"):
        stage_pass2_inference(run_rag, limit=limit)

    if start_idx <= STAGE_ORDER.index("compare"):
        stage_compare()

    pipeline_logger.info("orchestration", "pipeline_complete")
    print(f"\n{BAR}")
    print(f"  CodeGen pipeline complete.")
    print(f"{BAR}\n")


if __name__ == "__main__":
    main()
