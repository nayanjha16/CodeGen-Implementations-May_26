import os
from transformers import AutoTokenizer
from src.config import DATA, MODELS
from src.prompt_builder import build_text2sql_sample, build_sql2nosql_sample, build_text2nosql_sample
from finetune_unified import _build_unified_dataset
from src.loader import load_spider_tasks, load_spider_schema_maps, load_docspider_tasks, load_schema_context_map

# 1. Initialize Tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODELS["codegen"]["model_id"])
if tokenizer.pad_token is None: 
    tokenizer.pad_token = tokenizer.eos_token

print("🚀 Loading data collections for real-estate audit...")
spider_train = load_spider_tasks(DATA["spider_train"])
docspider_train = load_docspider_tasks(DATA["docspider_train"])
spider_schemas = load_spider_schema_maps()
docspider_schemas = load_schema_context_map(DATA["docspider_collections"])

# 2. Compile the Actual Dataset
print("🧠 Simulating multi-task compilation loop (with RAG checks)...")
max_sequence_ceiling = 2048

dataset = _build_unified_dataset(
    spider_tasks=spider_train,
    docspider_tasks=docspider_train,
    spider_schemas=spider_schemas,
    docspider_schemas=docspider_schemas,
    tokenizer=tokenizer,
    max_len=max_sequence_ceiling
)

# 3. Analyze Token Allocation and Formats
print("\n🔍 Auditing compiled token distributions...")
total_samples = len(dataset)
oversized_count = 0
task_distributions = {"NL-to-SQL": 0, "SQL-to-MQL": 0, "NL-to-MQL": 0}
visual_samples = {}
rag_active_count = 0

# String buffer to collect oversized alerts during iteration
alert_buffer = ""

for idx in range(total_samples):
    input_ids = dataset[idx]["input_ids"]
    token_len = len(input_ids)
    
    # Decode the actual token numbers back to a raw text string
    decoded_prompt = tokenizer.decode(input_ids, skip_special_tokens=False)
    
    if "### REFERENCE EXAMPLE ###" in decoded_prompt:
        rag_active_count += 1
        
    # Identify the task type via structural anchor substrings
    task_type = "Unknown"
    if "[Task: NL-to-SQL]" in decoded_prompt:
        task_type = "NL-to-SQL"
    elif "[Task: SQL-to-MQL]" in decoded_prompt:
        task_type = "SQL-to-MQL"
    elif "[Task: NL-to-MQL]" in decoded_prompt:
        task_type = "NL-to-MQL"
        
    if task_type != "Unknown":
        task_distributions[task_type] += 1

    # Check for catastrophic overflow leaks
    if token_len >= max_sequence_ceiling:
        oversized_count += 1
        alert_buffer += f"⚠️ [OVERSIZED SAMPLE ALERT] Index: {idx} | Task: {task_type} | Length: {token_len} Tokens\n"
        alert_buffer += f"{decoded_prompt}\n"
        alert_buffer += "-" * 80 + "\n\n"
        
    # Capture the first clean variant of each task type for explicit review
    if task_type not in visual_samples and token_len < max_sequence_ceiling:
        visual_samples[task_type] = decoded_prompt

# 4. Generate Reports for both Terminal and File Outputs
os.makedirs("logs", exist_ok=True)
output_log_path = "logs/prompt_inspection_dump.txt"

with open(output_log_path, "w", encoding="utf-8") as f_out:
    # Helper to print and write simultaneously
    def log_line(text=""):
        print(text)
        f_out.write(text + "\n")

    log_line("==================================================")
    log_line("📊 FINAL AUDIT PERFORMANCE REPORT")
    log_line("==================================================")
    log_line(f"Total Combined Training Samples:  {total_samples}")
    log_line(f"Oversized Violations Found:       {oversized_count} / {total_samples} ({(oversized_count/total_samples)*100:.2f}%)")
    log_line("\nTask Matrix Densities:")
    for task, count in task_distributions.items():
        log_line(f"  ▪️ {task:<12}: {count} samples")
    log_line("==================================================")
       
    log_line("\nRAG Headroom Telemetry:")
    log_line(f"  ▪️ RAG Retained (Fits)  : {rag_active_count} / {total_samples} samples")
    log_line(f"  ▪️ RAG Evicted (Dense)  : {total_samples - rag_active_count} samples")
    
    log_line("==================================================")

    log_line("\n👀 DISPLAYING VISUAL PROMPT SAMPLES FOR ARCHITECTURAL VERIFICATION:\n")
    for task, sample_text in visual_samples.items():
        log_line(f"--- [PROMPT LAYOUT SAMPLE: {task}] ---")
        # Write snippet to terminal but dump the full length structure to log file
        print(sample_text[:1200] + "\n\n... [Output Truncated for Terminal Clarity] ...\n")
        f_out.write(sample_text + "\n\n" + "="*80 + "\n\n")

    if oversized_count > 0:
        log_line("\n🚨 OVERSIZED SAMPLE DETAILS DUMP:")
        f_out.write(alert_buffer)
    else:
        log_line("\n✅ SUCCESS: 0 overflow samples detected across the compilation matrix.")

