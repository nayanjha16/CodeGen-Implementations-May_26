import time
from pathlib import Path
from text2sql.data.spider import SpiderDataset
from text2sql.data.bird import BirdDataset
from text2sql.pipeline import generate_for_examples
from text2sql.evaluate.runner import evaluate_results
from text2sql.report.writer import write_raw

def _load_dataset(dataset: str, spider_root: Path, bird_root: Path):
    if dataset == "spider":
        return SpiderDataset(root=spider_root, split="dev")
    if dataset == "bird":
        return BirdDataset(root=bird_root, split="dev")
    raise ValueError(f"unknown dataset: {dataset}")

def run_single(model_id, scenario, dataset, spider_root, bird_root, results_dir,
               metrics, sample_size, runner, retriever=None, judge_runner=None) -> Path:
    ds = _load_dataset(dataset, spider_root, bird_root)
    examples = ds.examples()
    if sample_size:
        examples = examples[:sample_size]
    db_ids = {e.db_id for e in examples}
    schemas = {db: ds.schema(db) for db in db_ids}
    db_paths = {db: ds.db_path(db) for db in db_ids}

    t0 = time.perf_counter()
    results = generate_for_examples(examples, schemas, db_paths, runner,
                                    scenario=scenario, retriever=retriever)
    t_gen = time.perf_counter()
    # dataset name ("spider"|"bird") is the benchmark key for dataset-aware EX semantics
    metric_vals = evaluate_results(results, db_path_fn=lambda db: db_paths[db],
                                   metrics=metrics, judge_runner=judge_runner,
                                   benchmark=dataset)
    t_eval = time.perf_counter()
    per_example = [{"db_id": r.example.db_id, "question": r.example.question,
                    "gold": r.example.gold_sql, "pred": r.sql} for r in results]
    meta = {
        "sample_size": sample_size,
        "n": len(results),
        "elapsed_seconds": round(t_eval - t0, 2),    # measured wall time for this cell
        "gen_seconds": round(t_gen - t0, 2),         # text-to-SQL generation
        "eval_seconds": round(t_eval - t_gen, 2),    # metric scoring (EX execution etc.)
        "finished_at": time.time(),
    }
    return write_raw(Path(results_dir) / "raw", model_id, scenario, dataset,
                     metric_vals, meta, per_example)
