"""CLI entry point for the text-to-SQL benchmark.

Examples:
    python run_experiments.py --model qwen3-coder-30b --scenario zero_shot --dataset spider
    python run_experiments.py --all
    python run_experiments.py --report
"""
import argparse
from pathlib import Path
from text2sql.config import load_config
from text2sql.orchestrator import run_single
from text2sql.models import make_runner
from text2sql.data.spider import SpiderDataset
from text2sql.data.bird import BirdDataset
from text2sql.data.retriever import ExampleRetriever, SentenceTransformerEmbedder
from text2sql.report.writer import aggregate_to_csv
from text2sql.report.charts import render_charts

SPIDER_ROOT = Path("data/spider/spider_data")
BIRD_ROOT = Path("data/bird/dev_20240627")

def _build_retriever(scenario, dataset, cfg):
    if scenario != "one_shot":
        return None
    # one-shot example pool: Spider uses its train split; BIRD has only dev locally,
    # so use BIRD dev as the pool (the retriever excludes the query's own question).
    if dataset == "spider":
        train = SpiderDataset(root=SPIDER_ROOT, split="train").examples()
    else:
        train = BirdDataset(root=BIRD_ROOT, split="dev").examples()
    if not train:
        return None
    return ExampleRetriever(train, embedder=SentenceTransformerEmbedder())

def _adapter_path(scenario, model_id, models_dir):
    if not scenario.startswith("finetuned_"):
        return None
    trained_on = scenario.replace("finetuned_", "")
    p = Path(models_dir) / f"{model_id}-{trained_on}-lora"
    return str(p) if p.exists() else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="experiments/config.yaml")
    ap.add_argument("--model"); ap.add_argument("--scenario"); ap.add_argument("--dataset")
    ap.add_argument("--finetune", action="store_true",
                    help="fine-tune --model on --dataset (spider|bird|combined)")
    ap.add_argument("--train-size", type=int, default=None,
                    help="cap fine-tune training examples (sample-first); default uses full train split")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    cfg = load_config(Path(args.config))
    results_dir = Path("results")

    if args.finetune:
        from text2sql.finetune import make_trainer
        from text2sql.finetune.orchestrator import prepare_finetune_data
        model_cfg = cfg.model(args.model)
        work = Path("models") / f"{args.model}-{args.dataset}-lora"
        train, valid = prepare_finetune_data(
            args.dataset, spider_root=SPIDER_ROOT, bird_root=BIRD_ROOT,
            out_dir=work / "data", max_examples=args.train_size)
        adapter = make_trainer(model_cfg).train(train, valid, work)
        print(f"adapter saved to {adapter}")
        return

    if args.report:
        csv = aggregate_to_csv(results_dir / "raw", results_dir / "reports" / "comparison.csv")
        render_charts(csv, results_dir / "reports" / "charts", metric="ex")
        print(f"Report written to {csv}")
        return

    jobs = cfg.experiments() if args.all else [
        {"model": args.model, "scenario": args.scenario, "dataset": args.dataset}]

    for job in jobs:
        raw = results_dir / "raw" / f"{job['model']}_{job['scenario']}_{job['dataset']}.json"
        if args.all and raw.exists():
            print(f"skip (exists): {raw.name}"); continue
        model_cfg = cfg.model(job["model"])
        adapter = _adapter_path(job["scenario"], job["model"], "models")
        runner = make_runner(model_cfg, adapter_path=adapter)
        judge = make_runner(cfg.model(cfg.evaluation["llm_judge_model"])) \
            if "llm_judge" in cfg.evaluation["metrics"] else None
        retriever = _build_retriever(job["scenario"], job["dataset"], cfg)
        out = run_single(job["model"], job["scenario"], job["dataset"],
                         spider_root=SPIDER_ROOT, bird_root=BIRD_ROOT,
                         results_dir=results_dir, metrics=cfg.evaluation["metrics"],
                         sample_size=cfg.evaluation["sample_size"], runner=runner,
                         retriever=retriever, judge_runner=judge)
        print(f"wrote {out}")

if __name__ == "__main__":
    main()
