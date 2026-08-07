"""
Unified Multi-Task Inference Runner for CodeGen.
Supports RAG and zero-shot evaluations across all three core operational tracks.

Usage:
    python run_multi_task_inference.py --task text2sql --rag
    python run_multi_task_inference.py --task sql2nosql --rag
    python run_multi_task_inference.py --task text2nosql --rag
"""

import argparse
import io
import json
import os
import subprocess
import sys
import torch
from contextlib import redirect_stdout

# Configuration and core imports
from src.config import MODELS, DATA, get_device_settings
from src.generator import initialize_model_and_tokenizer, generate_sql_prediction, generate_nosql_prediction
from src.processor import clean_generated_sql, clean_generated_nosql
from src.loader import (
    load_spider_tasks,
    load_spider_compact_schema_maps_with_fk,
    load_spider_table_names_map,
    load_docspider_tasks,
    load_schema_context_map,
)

# Dynamic fallback import for prompt hooks
import src.prompt_builder as pb

# Add execution directory to path for target isolation
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from stage5_evaluate_by_execution import evaluate_pipeline
except ImportError:
    evaluate_pipeline = None


# ---------------------------------------------------------------------------
# Task Evaluation Wrappers
# ---------------------------------------------------------------------------

def _run_spider_eval(predictions, output_dir, report_name):
    """Executes the standard Spider validation harness using match evaluation."""
    gold_txt = os.path.join(output_dir, "tmp_gold.txt")
    pred_txt = os.path.join(output_dir, "tmp_pred.txt")
    report_path = os.path.join(output_dir, report_name)

    with open(gold_txt, "w", encoding="utf-8") as f:
        for item in predictions:
            f.write(f"{item['gold_sql']}\t{item['db_id']}\n")

    with open(pred_txt, "w", encoding="utf-8") as f:
        for item in predictions:
            f.write(f"{item['predicted_sql']}\n")

    cmd = [
        sys.executable, "evaluation.py",
        "--gold", gold_txt,
        "--pred", pred_txt,
        "--db", os.path.join("data", "spider", "database"),
        "--table", DATA["spider_tables"],
        "--etype", "match",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    print("\n=== Spider Evaluation Results ===")
    output = result.stdout or result.stderr
    print(output)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"Report saved securely to: {report_path}")


def _run_docspider_eval(pred_path, output_dir, report_name):
    """Executes the functional DocSpider target test runtime via database assertion."""
    if evaluate_pipeline is None:
        print("[Warning] stage5_evaluate_by_execution.py not found. Skipping execution evaluation.")
        return

    buf = io.StringIO()
    with redirect_stdout(buf):
        try:
            evaluate_pipeline(pred_path)
        except Exception as e:
            print(f"Execution evaluation runtime error: {e}")
            
    report_text = buf.getvalue()
    print("\n=== DocSpider Execution Results ===")
    print(report_text)

    report_path = os.path.join(output_dir, report_name)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"Report saved securely to: {report_path}")


# ---------------------------------------------------------------------------
# Main Multi-Task Orchestrator
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Unified Multi-Task CodeGen Evaluation Harness")
    parser.add_argument(
        "--task", 
        required=True, 
        choices=["text2sql", "sql2nosql", "text2nosql"],
        help="Target processing task route to evaluate."
    )
    parser.add_argument(
        "--rag", 
        action="store_true", 
        help="Inject contextual top-1 training shots into prompt payloads using hybrid retrieval."
    )
    parser.add_argument(
        "--checkpoint_override",
        default=None,
        help="Path to an alternative adapter checkpoint directory."
    )
    parser.add_argument(
        "--output_dir",
        default=None,
        help="Override the output directory for predictions and reports. Defaults to config value."
    )
    parser.add_argument(
        "--limit",
        default=None, type=int,
        help="Cap number of inference samples (sanity testing)."
    )
    args = parser.parse_args()

    # Configuration Binding
    cfg = MODELS["codegen"]
    dev = get_device_settings()
    device = dev["device"]

    # Select output directory — CLI override takes priority, then config, then fallback
    output_dir = args.output_dir or cfg.get(f"output_{args.task}", os.path.join("outputs", f"codegen_{args.task}"))
    suffix = "_rag" if args.rag else ""
    pred_filename = f"predictions{suffix}.json"
    report_name = f"evaluation_report{suffix}.txt"

    os.makedirs(output_dir, exist_ok=True)
    pred_path = os.path.join(output_dir, pred_filename)

    # 1. Load Datasets and Metadata Context Schemas Dynamically
    print(f"⚙️ Preparing evaluation context for task: [{args.task.upper()}]...")
    if args.task == "text2sql":
        tasks = load_spider_tasks(DATA["spider_dev"])
        schema_maps = load_spider_compact_schema_maps_with_fk()
    else:
        tasks = load_docspider_tasks(DATA["docspider_dev"])
        schema_maps = load_schema_context_map(DATA["docspider_collections"])

    if args.limit:
        tasks = tasks[:args.limit]
        print(f"[inference] Sanity limit: running on {len(tasks)} samples only.")

    # 2. Configure Unified RAG Retrievers
    retriever = None
    table_names_map = None
    if args.rag:
        from src.retriever import Retriever
        retriever = Retriever(task=args.task)
        if args.task == "text2sql":
            table_names_map = load_spider_table_names_map()

    # Schema pruner — trims each prompt's schema to relevant tables only.
    # Requires: python scripts/build_retrieval_index.py --task schema
    schema_pruner = None
    try:
        from src.schema_pruner import SchemaPruner
        from src.loader import load_spider_fk_neighbors_map
        fk_neighbors  = load_spider_fk_neighbors_map()
        schema_pruner = SchemaPruner(fk_neighbors=fk_neighbors)
        print("✂️  Schema pruner loaded.")
    except Exception as _prune_err:
        print(f"⚠️  Schema pruner unavailable ({_prune_err}). Using full schemas.")

    # 3. Model Weight Initialization
    # Targets our unified multi-task adapter layout explicitly
    model, tokenizer = initialize_model_and_tokenizer(
        stage='unified', 
        adapter_path=args.checkpoint_override
    )

    predictions = []
    print(f"🚀 Starting inference sweep over {len(tasks)} examples...")

    for idx, task in enumerate(tasks):
        db_id = task.get("db_id", "")
        question = task.get("question", "")
        
        # Safe extraction hooks for target inputs
        gold_sql = task.get("query" if args.task == "text2sql" else "spider_gold_sql", "").strip()
        gold_mql = task.get("query", "").strip() if args.task != "text2sql" else ""

        # Fetch Contextual RAG Shot
        retrieved_example = None
        if retriever:
            if args.task == "text2sql":
                table_names = table_names_map.get(db_id, [])
                results = retriever.retrieve_text2sql(question, db_id, table_names, k=1)
            elif args.task == "text2nosql":
                # Safely collect collection names from the target map values
                collections = schema_maps.get(db_id, [])
                results = retriever.retrieve_text2nosql(question, db_id, collections, k=1)
            else:  # sql2nosql
                results = retriever.retrieve_sql2nosql(gold_sql, k=1)
                
            retrieved_example = results[0] if results else None

# 4. Prompt Builder Matrix Routing
        if args.task == "text2sql":
            prompt, _ = pb.build_text2sql_sample(
                "codegen", question, db_id, "", schema_maps,
                for_inference=True, retrieved_example=retrieved_example,
                schema_pruner=schema_pruner,
            )
            raw_output = generate_sql_prediction(model, tokenizer, prompt, is_unified=True)
            predicted_payload = clean_generated_sql(raw_output)
            
            predictions.append({
                "db_id": db_id,
                "question": question,
                "gold_sql": gold_sql,
                "predicted_sql": predicted_payload,
                "raw_generation": raw_output, # <-- CRITICAL FOR PHASE 2 TEACHER ANALYSIS
            })

        elif args.task == "sql2nosql":
            prompt, _ = pb.build_sql2nosql_sample(
                "codegen", gold_sql, db_id, "", schema_maps,
                for_inference=True, retrieved_example=retrieved_example,
                schema_pruner=schema_pruner,
            )
            raw_output = generate_nosql_prediction(model, tokenizer, prompt)
            predicted_payload = clean_generated_nosql(raw_output)
            
            predictions.append({
                "db_id": db_id,
                "question": question,
                "gold_sql": gold_sql,
                "gold_mql": gold_mql,
                "predicted_mql": predicted_payload,
                "raw_generation": raw_output, # <-- CRITICAL FOR PHASE 2 TEACHER ANALYSIS
            })

        elif args.task == "text2nosql":
            # Remove the hardcoded fallback; fail loudly if the prompt builder is missing
            build_fn = getattr(pb, "build_text2nosql_sample", None)
            if not build_fn:
                raise ImportError("Critical Error: build_text2nosql_sample is missing from prompt_builder.py. Cannot guarantee structural alignment.")
                
            prompt, _ = build_fn(
                "codegen", question, db_id, "", schema_maps,
                for_inference=True, retrieved_example=retrieved_example,
                schema_pruner=schema_pruner,
            )
            
            raw_output = generate_nosql_prediction(model, tokenizer, prompt)
            predicted_payload = clean_generated_nosql(raw_output)
            
            predictions.append({
                "db_id": db_id,
                "question": question,
                "gold_mql": gold_mql,
                "predicted_mql": predicted_payload,
                "raw_generation": raw_output, # <-- CRITICAL FOR PHASE 2 TEACHER ANALYSIS
            })

        # Save checking records incrementally to protect execution traces
        with open(pred_path, "w", encoding="utf-8") as f:
            json.dump(predictions, f, indent=2)

        if (idx + 1) % 50 == 0:
            print(f" Progress Checkpoint: {idx + 1}/{len(tasks)} samples processed.")

    print(f"\n✨ Inference completed. Raw records stored at: {pred_path}")

    # 5. Route to Target Metrics Evaluation Engine
    if args.task == "text2sql":
        _run_spider_eval(predictions, output_dir, report_name)
    else:
        _run_docspider_eval(pred_path, output_dir, report_name)


if __name__ == "__main__":
    main()