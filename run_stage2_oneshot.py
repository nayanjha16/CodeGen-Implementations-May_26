# run_stage2_oneshot.py
import json
import os
import torch
from src.config import DATASET_PATH

from src.loader import load_spider_schema_maps, load_spider_tasks, construct_one_shot_prompt
from src.generator import initialize_model_and_tokenizer, generate_sql_prediction
from src.processor import clean_generated_sql

def main():
    print("🚀 Initializing Stage 2 One-Shot Inference Engine (Spider 1.0 Dev Split)...")
    
    # 1. Load active DDL database schemas
    try:
        schema_map = load_spider_schema_maps()
        print(f"✅ Database schemas parsed and indexed successfully. Total DBs: {len(schema_map)}")
    except Exception as e:
        print(f"❌ Failed to parse schemas from tables.json: {e}")
        return

    # 2. Load all 1,034 Spider 1.0 verification tasks
    # NOTE: DATASET_PATH points to data/spider/dev.json containing your validation set.
    target_dataset = DATASET_PATH    
    try:
        tasks = load_spider_tasks(target_dataset, limit=None) # Set limit=5 if you want a fast sanity run first!
        print(f"📋 Loaded {len(tasks)} target queries from evaluation split.")
    except Exception as e:
        print(f"❌ Failed to load target validation file: {e}")
        return

    # 3. Spin up CodeGen weights onto the active GPU environment
    print("\n🤖 Loading Salesforce/codegen-350M-multi models onto accelerator context...")
    model, tokenizer = initialize_model_and_tokenizer()
    print("-" * 70)

    evaluation_results = []
    OUTPUT_PAYLOAD_PATH = "outputs/stage2_one_shot/stage2_predictions.json"

    # 4. Stream tasks through the Dynamic One-Shot Prompt Layer
    print(f"✍️ Commencing one-shot greedy generation loop...")
    for idx, task in enumerate(tasks):
        # Extract metadata identifiers unique to Spider 1.0 format
        question = task.get("question", "")
        db_id = task.get("db_id", "unknown_db")
        
        # Build prompt using the Dynamic Schema + Static Example function
        prompt_text = construct_one_shot_prompt(task, schema_map)
        
        # Execute causal completion prediction on GPU
        raw_prediction = generate_sql_prediction(model, tokenizer, prompt_text)
        
        # Extract pure text SQL statements and strip formatting noise
        final_sql = clean_generated_sql(raw_prediction)
        
        # Print progress bar tracking to monitoring screen
        if (idx + 1) % 50 == 0 or (idx + 1) == len(tasks) or (idx < 5):
            print(f" [{idx+1:04d}/{len(tasks)}] DB: {db_id:<15} -> Out: {final_sql[:50]}...")

        evaluation_results.append({
            "question": question,
            "db_id": db_id,
            "prompt_fed": prompt_text,
            "predicted_sql": final_sql
        })

    # 5. Output raw text translations out to a dedicated stage 2 results sheet
    os.makedirs(os.path.dirname(OUTPUT_PAYLOAD_PATH), exist_ok=True)
    with open(OUTPUT_PAYLOAD_PATH, "w", encoding="utf-8") as f:
        json.dump(evaluation_results, f, indent=4)

    print("=" * 70)
    print("🎉 Stage 2 One-Shot Generation Execution Vector Finalized!")
    print(f"💾 Active output predictions saved securely to: {OUTPUT_PAYLOAD_PATH}")
    print("=" * 70)

if __name__ == "__main__":
    main()