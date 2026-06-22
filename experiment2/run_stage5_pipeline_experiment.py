# run_stage5_pipeline_experiment.py
import os
import json
import torch
from datetime import datetime
from peft import PeftModel

from src.config import (
    DOCSPIDER_DEV_PATH,
    DOCSPIDER_COLLECTIONS_PATH,
    EXP2_NOSQL_CHECKPOINT_PATH,
    EXP2_PIPELINE_OUTPUT_PATH
)
from src.loader import load_spider_tasks, load_schema_context_map, construct_nosql_prompt
from src.generator import initialize_model_and_tokenizer
from src.processor import clean_generated_nosql

def main():
    print("📥 [STAGE 5] Launching Schema-Grounded NoSQL Evaluation Pipeline...")
    
    # 1. Load your evaluation subset tasks
    eval_tasks = load_spider_tasks(DOCSPIDER_DEV_PATH, limit=None)
    
    # 2. Base weight compilation configuration
    base_model, tokenizer = initialize_model_and_tokenizer(stage='exp2')
    
    os.makedirs(os.path.dirname(EXP2_PIPELINE_OUTPUT_PATH), exist_ok=True)
    
    # 3. Load schema metadata tracking structures
    schema_context_map = load_schema_context_map(DOCSPIDER_COLLECTIONS_PATH)
    
    print(f"🔩 Loading Grounded Module 2 Adapter from: {EXP2_NOSQL_CHECKPOINT_PATH}")
    
    # Determine local hardware footprint safely
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Load adapter with dynamic hardware allocation maps
    model = PeftModel.from_pretrained(
        base_model, 
        EXP2_NOSQL_CHECKPOINT_PATH,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map="auto" if device == "cuda" else None
    )
    model.eval()
    
    pipeline_results = []
    
    print("\n🚀 Streaming test queries through processing matrix...")
    for idx, task in enumerate(eval_tasks):
        db_id = task.get("db_id", "")
        gold_sql = task.get("spider_gold_sql", "")
        question = task.get("question", "")
        
        print(f" 🔍 [{idx+1}/5] Processing DB: {db_id} | Query: '{question[:40]}...'")
        
        # Build the grounded prompt matching the training syntax precisely
        nosql_prompt = construct_nosql_prompt(gold_sql, db_id, schema_context_map)
        
        # Build input matrices and move them explicitly to the model's physical execution block
        inputs = tokenizer(nosql_prompt, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=128,
                temperature=0.0,
                do_sample=False,
                repetition_penalty=1.2,
                no_repeat_ngram_size=4,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        # Isolate target execution tokens from input sequence lengths
        raw_nosql_output = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        predicted_mql = clean_generated_nosql(raw_nosql_output)
        
        pipeline_results.append({
            "db_id": db_id,
            "question": question,
            "gold_sql": gold_sql,
            "gold_mql": task.get("query", ""),
            "intermediate_predicted_sql": gold_sql,
            "predicted_mql": predicted_mql
        })
                
        # Write outputs continuously to safeguard state
        with open(EXP2_PIPELINE_OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(pipeline_results, f, indent=4)

    print(f"\n✅ Pipeline complete! Grounded evaluations written to: {EXP2_PIPELINE_OUTPUT_PATH}")

if __name__ == "__main__":
    main()