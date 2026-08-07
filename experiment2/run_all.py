"""
Master orchestrator — runs fine-tuning, inference, evaluation, and comparison
for one or both models on one, two, or all three tasks in sequence.

Usage examples:
    python run_all.py                               # All models, all 3 tasks
    python run_all.py --model_type codegen          # CodeGen unified multi-task only
    python run_all.py --task text2nosql             # Direct NL -> MQL track only
    python run_all.py --skip_train --rag            # Multi-task RAG inference sweep
"""

import argparse
import subprocess
import sys
import os
from datetime import datetime
from src.logger import pipeline_logger


def _run(script, *extra_args, label=""):
    cmd = [sys.executable, script] + list(extra_args)
    header = label or f"python {script} {' '.join(extra_args)}"
    bar = "=" * 70
    start_ts = datetime.now().strftime("%H:%M:%S")
    print(f"\n{bar}")
    print(f"  STEP [{start_ts}]: {header}")
    print(f"{bar}\n")
    pipeline_logger.info("orchestration", "step_start", stats={
        "label": header,
        "cmd": " ".join(cmd),
        "start_time": start_ts
    })
    result = subprocess.run(cmd)
    end_ts = datetime.now().strftime("%H:%M:%S")
    if result.returncode != 0:
        pipeline_logger.error("orchestration", "step_failed", stats={
            "label": header,
            "exit_code": result.returncode,
            "end_time": end_ts
        })
        print(f"\n[run_all] ERROR in step '{header}' (exit {result.returncode}). Stopping.")
        sys.exit(result.returncode)
    pipeline_logger.info("orchestration", "step_complete", stats={
        "label": header,
        "exit_code": 0,
        "end_time": end_ts
    })


def main():
    parser = argparse.ArgumentParser(description="End-to-end multi-task experiment runner")
    parser.add_argument(
        "--model_type",
        choices=["codegen", "codet5"],
        default=None,
        help="Run one model type only. Omit to run both.",
    )
    parser.add_argument(
        "--task",
        choices=["text2sql", "sql2nosql", "text2nosql"],
        default=None,
        help="Run one specific task track only. Omit to run all three.",
    )
    parser.add_argument(
        "--skip_train",
        action="store_true",
        help="Skip fine-tuning phase (evaluate existing checkpoints directly).",
    )
    parser.add_argument(
        "--skip_eval",
        action="store_true",
        help="Skip inference and metric evaluation passes (fine-tune only).",
    )
    parser.add_argument(
        "--rag",
        action="store_true",
        help="Inject contextual top-1 target examples into evaluation prompts.",
    )
    args = parser.parse_args()

    models = [args.model_type] if args.model_type else ["codegen", "codet5"]
    tasks  = [args.task]       if args.task        else ["text2sql", "sql2nosql", "text2nosql"]

    pipeline_logger.info("orchestration", "experiment_start", stats={
        "models": models,
        "tasks": tasks,
        "skip_train": args.skip_train,
        "skip_eval": args.skip_eval,
        "rag": args.rag
    })

    # -----------------------------------------------------------------------
    # Phase 1: Fine-Tuning Execution Block
    # -----------------------------------------------------------------------
    if not args.skip_train:
        pipeline_logger.info("orchestration", "phase1_finetuning_start", stats={"models": models})

        # 1. Execute Unified Multi-Task Training for CodeGen
        if "codegen" in models:
            _run("finetune_unified.py", label="Unified Multi-Task Fine-Tuning: CodeGen-350M")

        # 2. Execute Legacy Single-Task Training for CodeT5
        if "codet5" in models:
            for task in tasks:
                script = f"finetune_{task}.py"
                if not os.path.exists(script):
                    pipeline_logger.warning("orchestration", "script_not_found", stats={"script": script})
                    print(f"[run_all] Skipping training step: '{script}' not found for CodeT5.")
                    continue
                _run(script, "--model_type", "codet5", label=f"Fine-tune CodeT5 on track: {task}")

        pipeline_logger.info("orchestration", "phase1_finetuning_done")
    else:
        pipeline_logger.info("orchestration", "phase1_skipped", stats={"reason": "--skip_train"})
        print("[run_all] --skip_train flag enabled — skipping all fine-tuning workflows.")

    # -----------------------------------------------------------------------
    # Phase 2: Multi-Task Inference & Verification
    # -----------------------------------------------------------------------
    if not args.skip_eval:
        rag_flag  = ["--rag"] if args.rag else []
        rag_label = " +RAG" if args.rag else ""

        pipeline_logger.info("orchestration", "phase2_inference_start", stats={
            "models": models, "tasks": tasks, "rag": args.rag
        })

        for task in tasks:
            for mt in models:
                if mt == "codegen":
                    # CodeGen routes entirely through the new unified engine
                    _run(
                        "run_multi_task_inference.py",
                        "--task", task,
                        *rag_flag,
                        label=f"Unified Multi-Task Inference: CodeGen -> {task}{rag_label}"
                    )
                else:
                    # CodeT5 maintains legacy isolated script routing
                    script = f"run_inference_{task}.py"
                    if not os.path.exists(script):
                        pipeline_logger.warning("orchestration", "script_not_found", stats={"script": script})
                        print(f"[run_all] Skipping evaluation step: Legacy script '{script}' not found for CodeT5.")
                        continue

                    _run(
                        script,
                        "--model_type", mt,
                        *rag_flag,
                        label=f"Legacy Inference + Eval: CodeT5 -> {task}{rag_label}"
                    )

        # Generate matrix summary report if execution state allows it
        _run("compare_results.py", label="Generate comprehensive cross-model comparison report")
        pipeline_logger.info("orchestration", "phase2_inference_done")
    else:
        pipeline_logger.info("orchestration", "phase2_skipped", stats={"reason": "--skip_eval"})
        print("[run_all] --skip_eval flag enabled — skipping evaluation generation blocks.")

    pipeline_logger.info("orchestration", "experiment_complete")
    print("\n[run_all] Complete experiment iteration execution completed successfully.")


if __name__ == "__main__":
    main()