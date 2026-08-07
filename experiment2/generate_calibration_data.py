"""
Intermediate Dataset Preprocessing Pipeline.
Uses a Teacher LLM to generate Calibration Data (Broken Drafts + Analysis) 
from the original Spider dataset.

Usage:
    export OPENAI_API_KEY="your-key"
    python generate_calibration_data.py --input_path data/train.json --output_path data/spider_augmented_train.json
"""

import argparse
import json
import os
import time
from tqdm import tqdm
from openai import OpenAI

# Initialize client safely
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "mock-key"))

TEACHER_PROMPT_TEMPLATE = """
You are an expert database compiler and teacher. Your task is to analyze a correct target SQL query, generate a realistic "broken draft" that a junior engineer might write, and provide a 1-sentence diagnostic analysis of the mistake.

Database Schema Context:
{schema}

Natural Language User Question:
{question}

Correct Target SQL (Gold Standard):
{gold_sql}

Provide your response in strict JSON format with exactly two keys:
1. "broken_draft": A SQL query that looks plausible but contains a specific logical error (e.g., missing a JOIN condition, using the wrong aggregate function, incorrect WHERE clause filter, or misaligned GROUP BY statement).
2. "teacher_analysis": A single, dense sentence pointing out the schema or logic alignment mismatch and how to resolve it. Do not reference the text "broken draft" explicitly; speak directly to the architectural rule broken.

Response JSON:
"""

def call_teacher_llm(question, schema, gold_sql):
    """Queries the Teacher LLM to get calibration data targets."""
    # Fallback pattern if API key is unpopulated for structural testing
    if os.environ.get("OPENAI_API_KEY") is None:
        return {
            "broken_draft": "SELECT name FROM artist WHERE id = 1;",
            "teacher_analysis": "Fallback: Ensure explicit table identifiers are mapped across foreign join targets."
        }

    formatted_prompt = TEACHER_PROMPT_TEMPLATE.format(
        schema=schema,
        question=question,
        gold_sql=gold_sql
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Cost-effective and highly reliable for structured syntax manipulation
            messages=[{"role": "user", "content": formatted_prompt}],
            response_format={"type": "json_object"},
            temperature=0.4 # Kept low to keep the structured errors grounded and realistic
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"\n[Warning] API call failed, generating procedural fallback: {e}")
        return {
            "broken_draft": gold_sql.replace("SELECT", "SELECT DISTINCT") if "DISTINCT" not in gold_sql else "SELECT * FROM fallback;",
            "teacher_analysis": "Verify tracking constraints and condition predicates."
        }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", default="data/train.json", help="Path to original spider train data")
    parser.add_argument("--schema_path", default="data=tables.json", help="Path to spider schema tables file")
    parser.add_argument("--output_path", default="data/spider_augmented_train.json")
    args = parser.parse_args()

    print(f"[Upstream Pipeline] Starting data augmentation on: {args.input_path}")
    
    # Load original tasks
    with open(args.input_path, "r") as f:
        tasks = json.load(f)

    # For safety during large runs, we slice or loop defensively
    augmented_tasks = []
    
    # Process through the intermediate LLM execution step
    for entry in tqdm(tasks[:1000], desc="Teacher Synthesis Step"): # Adjust slicing to run full distributions
        # Extract metadata metrics safely
        question = entry.get("question", "")
        gold_sql = entry.get("query", "")
        db_id = entry.get("db_id", "")
        
        # Pulling schema summary context string (Mocked here, adapt to your schema map lookup)
        schema_summary = f"Database: {db_id}. Contains related system catalogs."

        # Execute intermediate transformation
        calibration = call_teacher_llm(question, schema_summary, gold_sql)
        
        # Inject custom calibration metrics directly into a copy of the original dataset structure
        entry["broken_draft"] = calibration.get("broken_draft", "")
        entry["teacher_analysis"] = calibration.get("teacher_analysis", "")
        
        augmented_tasks.append(entry)
        
        # Rate-limiting mitigation heartbeat
        time.sleep(0.05)

    # Save the new intermediate dataset state
    with open(args.output_path, "w") as f:
        json.dump(augmented_tasks, f, indent=4)
        
    print(f"[Upstream Pipeline] Step complete. Augmented dataset saved to: {args.output_path}")

if __name__ == "__main__":
    main()