# test_sanity.py
import sys
from transformers import AutoTokenizer
from finetune_unified import _build_unified_dataset
from src.loader import load_spider_tasks, load_spider_schema_maps, load_docspider_tasks, load_schema_context_map
from src.config import DATA, MODELS

print("🛰️ Loading baseline tokenization layouts...")
cfg = MODELS["codegen"]
tokenizer = AutoTokenizer.from_pretrained(cfg["model_id"])

# Force a dummy pad token if not set to prevent collator issues
if tokenizer.pad_token_id is None:
    tokenizer.pad_token = tokenizer.eos_token

print("📂 Sampling minimal data blocks...")
spider_tasks = load_spider_tasks(DATA["spider_train"])[:5]
docspider_tasks = load_docspider_tasks(DATA["docspider_train"])[:5]
spider_schemas = load_spider_schema_maps()
docspider_schemas = load_schema_context_map(DATA["docspider_collections"])

print("🧱 Compiling unified multi-task dataset matrix...")
try:
    dataset = _build_unified_dataset(
        spider_tasks, docspider_tasks, spider_schemas, docspider_schemas, 
        tokenizer, max_len=cfg.get("max_input_len_rag", 1024)
    )
    print(f"✅ Success! Compiled {len(dataset)} balanced multi-task samples.")
    print(f"   First sample check -> input_ids len: {len(dataset[0]['input_ids'])}, labels len: {len(dataset[0]['labels'])}")
    
    # Verify exact target label masking consistency
    labels = dataset[0]['labels']
    masked_count = labels.count(-100)
    print(f"   Prompt Causal Masking: {masked_count} tokens hidden, {len(labels) - masked_count} tokens target-optimized.")
except Exception as e:
    print(f"❌ Data pipeline compilation failed: {str(e)}")