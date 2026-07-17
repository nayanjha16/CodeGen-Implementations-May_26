#!/usr/bin/env python3
"""End-to-end benchmark runner for NL2Py and Java2Py tasks."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "inference"))
sys.path.insert(0, str(PROJECT_ROOT / "data" / "scripts"))

from datasets import load_from_disk

from evaluation.executor import CodeExecutor
from evaluation.metrics import compute_all_metrics
from generator import load_generator
from prompt_templates import format_java2py_inference, format_nl2py_inference
from rag_pipeline import RAGPipeline

RESULTS_DIR = PROJECT_ROOT / "results"


def load_eval_dataset(task: str, split: str = "val"):
    dataset_path = PROJECT_ROOT / "data" / "processed" / task / split
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {dataset_path}. Run preprocess script first."
        )
    return load_from_disk(str(dataset_path))


def generate_predictions(
    task: str,
    dataset,
    max_samples: int,
    use_rag: bool,
    use_api: bool,
    api_url: str,
):
    predictions = []
    references = []
    inputs = []
    execution_payloads = []

    samples = list(range(min(max_samples, len(dataset))))

    if use_api:
        import httpx
        endpoint = f"{api_url}/{task}"
        client = httpx.Client(timeout=120.0)
        for i in samples:
            item = dataset[i]
            if task == "nl2py":
                body = {"query": item["nl_query"], "use_rag": use_rag}
            else:
                body = {"java_code": item["java_code"], "use_rag": use_rag}
            resp = client.post(endpoint, json=body)
            resp.raise_for_status()
            pred = resp.json()["code"]
            ref = item["python_code"]
            predictions.append(pred)
            references.append(ref)
            inputs.append(item.get("nl_query") or item.get("java_code", ""))
            execution_payloads.append({"code": pred, "reference": ref})
        client.close()
    else:
        generator = load_generator(task)
        rag = RAGPipeline(task=task) if use_rag else None

        for i in samples:
            item = dataset[i]
            if task == "nl2py":
                if rag:
                    prompt = rag.build_prompt(item["nl_query"])
                else:
                    prompt = format_nl2py_inference(item["nl_query"])
            else:
                if rag:
                    prompt = rag.build_prompt(item["java_code"])
                else:
                    prompt = format_java2py_inference(item["java_code"])

            pred = generator.generate(prompt)
            ref = item["python_code"]
            predictions.append(pred)
            references.append(ref)
            inputs.append(item.get("nl_query") or item.get("java_code", ""))
            execution_payloads.append({"code": pred, "reference": ref})

    return predictions, references, inputs, execution_payloads


def run_execution(execution_payloads: list[dict], run_sandbox: bool) -> list[dict]:
    if not run_sandbox:
        return []
    executor = CodeExecutor(use_docker=True)
    results = []
    for payload in execution_payloads:
        result = executor.execute(payload["code"])
        results.append(result)
    return results


def print_report(report: dict):
    print("\n" + "=" * 60)
    print("EVALUATION REPORT")
    print("=" * 60)
    for key, value in sorted(report.items()):
        if isinstance(value, float):
            print(f"  {key:30s}: {value:.4f}")
        elif key != "samples" and key != "timestamp":
            print(f"  {key:30s}: {value}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Run evaluation benchmark")
    parser.add_argument("--task", choices=["nl2py", "java2py"], required=True)
    parser.add_argument("--split", default="val", choices=["train", "val"])
    parser.add_argument("--max-samples", type=int, default=50)
    parser.add_argument("--use-rag", action="store_true", default=False)
    parser.add_argument("--use-api", action="store_true", help="Call FastAPI instead of local model")
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--run-sandbox", action="store_true", help="Run execution accuracy tests")
    parser.add_argument("--skip-bert", action="store_true", help="Skip slow BERTScore metrics")
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    print(f"Loading {args.task} {args.split} dataset...")
    dataset = load_eval_dataset(args.task, args.split)

    print(f"Generating predictions for {min(args.max_samples, len(dataset))} samples...")
    predictions, references, inputs, exec_payloads = generate_predictions(
        task=args.task,
        dataset=dataset,
        max_samples=args.max_samples,
        use_rag=args.use_rag,
        use_api=args.use_api,
        api_url=args.api_url,
    )

    print("Computing metrics...")
    execution_results = run_execution(exec_payloads, args.run_sandbox)
    metrics = compute_all_metrics(
        predictions,
        references,
        execution_results=execution_results if execution_results else None,
        skip_bert=args.skip_bert,
    )

    report = {
        "task": args.task,
        "split": args.split,
        "num_samples": len(predictions),
        "use_rag": args.use_rag,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **metrics,
        "samples": [
            {
                "input": inputs[i][:200],
                "prediction": predictions[i][:500],
                "reference": references[i][:500],
                "execution_passed": (
                    execution_results[i].get("passed") if execution_results else None
                ),
            }
            for i in range(len(predictions))
        ],
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = args.output or str(
        RESULTS_DIR / f"eval_{args.task}_{args.split}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print_report({k: v for k, v in report.items() if k != "samples"})
    print(f"\nFull report saved to {output_path}")


if __name__ == "__main__":
    main()
