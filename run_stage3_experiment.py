import json
import os
import time
from src.config import DATASET_PATH, STAGE3_OUTPUT_PATH
from src.loader import load_spider_tasks, construct_stage3_prompt
from src.generator import initialize_model_and_tokenizer, generate_sql_prediction

def run_stage3_pipeline(tasks, model, tokenizer, output_file_path):
    print("\n" + "="*70)
    print(f"🎬 Starting Full STAGE 3 Fine-Tuned LoRA Pipeline on {len(tasks)} Spider Tasks...")
    print("="*70)
    
    results = []
    start_time = time.time()
    
    for idx, task in enumerate(tasks):
        # 1. Generate the precise fine-tuning prompt structure (ignoring heavy schema strings)
        prompt_text = construct_stage3_prompt(task)
        
        # 2. Run model inference using our adapter-fused model
        raw_prediction = generate_sql_prediction(model, tokenizer, prompt_text)
        
        # 3. Clean up the response
        # (Since your native generator already strips out input_len tokens, 
        # raw_prediction will contain exactly the pure generated SQL answer!)
        final_sql = raw_prediction.strip()
        
        # Print rapid progress checks
        if (idx + 1) % 10 == 0 or (idx + 1) == len(tasks):
            elapsed = time.time() - start_time
            print(f" [STAGE 3 LoRA] Processed {idx+1}/{len(tasks)} tasks... (Elapsed: {elapsed:.1f}s)")
            
        results.append({
            "db_id": task.get("db_id"),
            "question": task.get("question"),
            "gold_query": task.get("query"),
            "predicted_sql": final_sql
        })
        
    # Ensure folder path exists and save results
    output_dir = os.path.dirname(output_file_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
        
    print(f"✅ Finished! Stage 3 fine-tuned predictions written to: '{output_file_path}'")

def main():
    start_total_time = time.time()
    
    # 1. Load your verification validation tasks
    try:
        # Keeping your verification limit of None, change to 5 for quick testing on 5 samples.
        all_tasks = load_spider_tasks(DATASET_PATH, limit=None) 
    except FileNotFoundError as e:
        print(e)
        return

    # 2. Spin up the model environment passing the stage 3 flag
    model, tokenizer = initialize_model_and_tokenizer(stage=3)
    
    # 3. Run Experiment: Stage 3 Fine-Tuned Inference
    run_stage3_pipeline(
        tasks=all_tasks,
        model=model,
        tokenizer=tokenizer,
        output_file_path=STAGE3_OUTPUT_PATH
    )
    
    print("\n" + "="*70)
    print(f"🎉 Stage 3 Evaluation complete in {(time.time() - start_total_time)/60:.2f} minutes!")
    print("="*70)

if __name__ == "__main__":
    main()