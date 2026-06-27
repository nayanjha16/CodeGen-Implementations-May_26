"""Load-once LLM-judge pass (7th metric). Runs DEAD LAST, after all evals + core report.

Loads the judge model (qwen3-coder-30b) ONCE and scores every results/raw/*.json cell
from its stored per_example preds, sample-limited to --limit examples/cell. Writes
metrics["llm_judge"] back into each cell so `run_experiments.py --report` adds the column.

CORROBORATING ONLY: EX stays the primary metric; judge scores never override EX.
SELF-PREFERENCE BIAS: the judge (qwen3-coder-30b) is itself under test and favors
qwen-family outputs — disclosed in the report, not corrected here.

    HF_HOME=... HF_HUB_OFFLINE=1 .venv/bin/python scripts/judge_pass.py --limit 75
"""
import argparse
import json
from pathlib import Path
from text2sql.config import load_config
from text2sql.models import make_runner
from text2sql.evaluate.llm_judge import judge_cell


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="experiments/inference.yaml")
    ap.add_argument("--limit", type=int, default=75, help="examples scored per cell (50-100)")
    ap.add_argument("--raw-dir", default="results/raw")
    ap.add_argument("--force", action="store_true", help="re-judge cells that already have llm_judge")
    ap.add_argument("--skip-collapsed", action="store_true",
                    help="skip finetuned cells of the large MLX models (qwen/deepseek/codestral) that "
                         "collapsed to degenerate output (EX~0); judging garbage wastes compute")
    args = ap.parse_args()

    # large MLX models whose LoRA fine-tunes collapsed (see RESULTS.md Stage A finding)
    COLLAPSED_MODELS = {"qwen3-coder-30b", "deepseek-coder-33b", "codestral-22b"}

    cfg = load_config(Path(args.config))
    judge_id = cfg.evaluation["llm_judge_model"]
    runner = make_runner(cfg.model(judge_id))  # loaded ONCE, reused across all cells
    print(f"judge loaded once: {judge_id}")

    for f in sorted(Path(args.raw_dir).glob("*.json")):
        d = json.loads(f.read_text())
        if args.skip_collapsed and d["model"] in COLLAPSED_MODELS and d["scenario"].startswith("finetuned"):
            print(f"skip (collapsed FT cell): {f.name}"); continue
        if "llm_judge" in d.get("metrics", {}) and not args.force:
            print(f"skip (already judged): {f.name}"); continue
        avg = judge_cell(d.get("per_example", []), runner, limit=args.limit)
        if avg is None:
            print(f"skip (no per_example): {f.name}"); continue
        d["metrics"]["llm_judge"] = avg
        d.setdefault("meta", {})["llm_judge_n"] = min(args.limit, len(d["per_example"]))
        f.write_text(json.dumps(d, indent=2))
        print(f"judged {f.name}: llm_judge={avg:.3f} (n={d['meta']['llm_judge_n']})")
    print("JUDGE PASS COMPLETE")


if __name__ == "__main__":
    main()
