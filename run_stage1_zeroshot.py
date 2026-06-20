# run_all_experiments.py
import json
import os
import time
from src.config import DATASET_PATH, OUTPUT_PATH
from src.loader import load_spider_tasks, load_spider_schema_maps, construct_zero_shot_prompt
from src.generator import initialize_model_and_tokenizer, generate_sql_prediction
from src.processor import clean_generated_sql

def run_pipeline(tasks, schema_map, model, tokenizer, output_file_path):
    print("\n" + "="*70)
    print(f"🎬 Starting Full ZERO-SHOT Baseline Pipeline on {len(tasks)} Spider Tasks...")
    print("="*70)
    
    results = []
    start_time = time.time()
    
    for idx, task in enumerate(tasks):
        # 1. Generate the specific prompt text passing the schema dictionary
        prompt_text = construct_zero_shot_prompt(task, schema_map)
        
        # 2. Run model inference
        raw_prediction = generate_sql_prediction(model, tokenizer, prompt_text)
        
        # 3. Process and clean the query
        final_sql = clean_generated_sql(raw_prediction)
        
        if (idx + 1) % 10 == 0 or (idx + 1) == len(tasks):
            elapsed = time.time() - start_time
            print(f" [ZERO-SHOT] Processed {idx+1}/{len(tasks)} tasks... (Elapsed: {elapsed:.1f}s)")
            
        results.append({
            "db_id": task.get("db_id"),
            "question": task.get("question"),
            "gold_query": task.get("query"),
            "predicted_sql": final_sql
        })
        
    # Ensure folder path exists and save
    output_dir = os.path.dirname(output_file_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
        
    print(f"✅ Finished! Output baseline written to: '{output_file_path}'")

def main():
    start_total_time = time.time()
    
    # 1. Load schema maps and tasks
    try:
        schema_map = load_spider_schema_maps()
        all_tasks = load_spider_tasks(DATASET_PATH, limit=5) # Set limit=10 for rapid verification tests
    except FileNotFoundError as e:
        print(e)
        return

    # 2. Spin up the model environment
    model, tokenizer = initialize_model_and_tokenizer()
    
    # 3. Run Experiment: Zero-Shot Baseline
    run_pipeline(
        tasks=all_tasks,
        schema_map=schema_map,
        model=model,
        tokenizer=tokenizer,
        output_file_path=OUTPUT_PATH
    )
    
    print("\n" + "="*70)
    print(f"🎉 Baseline complete in {(time.time() - start_total_time)/60:.2f} minutes!")
    print("="*70)

if __name__ == "__main__":
    main()