import torch

def get_device_settings():
    """
    Auto-detect runtime and return precision/device settings.
    CPU  -> float32, no mixed precision
    CUDA -> float16 (codegen) or bfloat16 (codet5) when supported
    """
    if torch.cuda.is_available():
        bf16_ok = torch.cuda.is_bf16_supported()
        return {
            "device":        "cuda",
            "codegen_dtype": torch.float16,
            "codet5_dtype":  torch.bfloat16 if bf16_ok else torch.float16,
            "codegen_fp16":  True,
            "codegen_bf16":  False,
            "codet5_fp16":   not bf16_ok,
            "codet5_bf16":   bf16_ok,
        }
    return {
        "device":        "cpu",
        "codegen_dtype": torch.float32,
        "codet5_dtype":  torch.float32,
        "codegen_fp16":  False,
        "codegen_bf16":  False,
        "codet5_fp16":   False,
        "codet5_bf16":   False,
    }


MODELS = {
    "codegen": {
        "model_id":              "Salesforce/codegen-350M-multi",
        "lora_targets":          ["qkv_proj", "out_proj", "fc_in", "fc_out"],
        "lora_r":                16,
        "lora_alpha":            32,
        "lora_dropout":          0.05,
        "epochs":                7,
        "train_batch":           1,
        "grad_accum":            16,              # effective batch = 16 (T4 OOM at train_batch>1)
        "lr":                    2e-4,
        "warmup_ratio":          0.03,
        "weight_decay":          0.01,
        "max_input_len":         2048,
        "max_target_len":        150,
        "num_beams":             4,
        # Separate checkpoints so Pass 1 weights are preserved for comparison
        "checkpoint_pass1":      "models/codegen_pass1",
        "checkpoint_pass2":      "models/codegen_pass2",
        # Separate output dirs so Pass 1 reports are not overwritten by Pass 2
        "output_text2sql":       "outputs/codegen/pass1/text2sql",
        "output_sql2nosql":      "outputs/codegen/pass1/sql2nosql",
        "output_text2nosql":     "outputs/codegen/pass1/text2nosql",
        "output_text2sql_p2":    "outputs/codegen/pass2/text2sql",
        "output_sql2nosql_p2":   "outputs/codegen/pass2/sql2nosql",
        "output_text2nosql_p2":  "outputs/codegen/pass2/text2nosql",
    },
    "codet5": {
        "model_id":             "Salesforce/codet5p-220m",
        "lora_targets":         ["q", "v"],      # T5 attention projection names
        "lora_r":               16,
        "lora_alpha":           32,
        "lora_dropout":         0.05,
        "epochs_text2sql":      10,              # from experiment 1
        "epochs_sql2nosql":     10,
        "train_batch":          4,
        "grad_accum":           4,               # effective batch = 16
        "lr":                   2e-4,
        "warmup_ratio":         0.03,
        "weight_decay":         0.01,
        "max_input_len":        512,
        "max_input_len_rag":    768,             # inference only — larger context for --rag
        "max_target_len":       256,             # from experiment 1
        "num_beams":            4,               # from experiment 1
        "checkpoint_text2sql":  "models/codet5_text2sql",
        "checkpoint_sql2nosql": "models/codet5_sql2nosql",
        "output_text2sql":      "outputs/codet5/text2sql",
        "output_sql2nosql":     "outputs/codet5/sql2nosql",
    },
}

DATA = {
    # Original datasets
    "spider_train":                   "data/spider/train_spider.json",
    "spider_dev":                     "data/spider/dev.json",
    "spider_tables":                  "data/spider/tables.json",
    "docspider_train":                "docspider/docspider_ground_truth_dataset/train.json",
    "docspider_dev":                  "docspider/docspider_ground_truth_dataset/dev.json",
    "docspider_collections":          "docspider/docspider_ground_truth_dataset/collections.json",
    # Pass 2 — failure records written by extract_failures.py
    "spider_failures":                "data/spider/text2sql_failures.json",
    "docspider_sql2nosql_failures":   "docspider/docspider_ground_truth_dataset/sql2nosql_failures.json",
    "docspider_text2nosql_failures":  "docspider/docspider_ground_truth_dataset/text2nosql_failures.json",
    # Pass 2 — teacher-annotated training sets written by generate_teacher_data.py
    "spider_augmented_train":         "data/spider/spider_augmented_train.json",
    "docspider_augmented_train":      "docspider/docspider_ground_truth_dataset/train_augmented.json",
}

# Teacher LLM — used by generate_teacher_data.py
TEACHER = {
    # provider: "groq" | "together" | "fireworks" | "openai" | "anthropic"
    # For groq/together/fireworks the OpenAI client is reused with base_url.
    "provider":           "groq",
    "base_url":           "https://api.groq.com/openai/v1",
    "model_id":           "llama-3.3-70b-versatile",
    # Alternatives:
    #   Groq  (free)       base_url="https://api.groq.com/openai/v1"
    #                      model_id="deepseek-r1-distill-llama-70b"
    #   Together (SQL)     base_url="https://api.together.xyz/v1"
    #                      model_id="defog/sqlcoder-70b-alpha"
    #   Together (coder)   base_url="https://api.together.xyz/v1"
    #                      model_id="Qwen/Qwen2.5-Coder-72B-Instruct"
    #   OpenAI             base_url=None, model_id="gpt-4o-mini"
    #   Anthropic          provider="anthropic", model_id="claude-haiku-4-5-20251001"
    "temperature":        0.2,
    "max_output_tokens":  450,
    "analysis_max_words": 35,
    "rate_limit_sleep":   0.1,            # seconds between API calls
    "max_failures":       3000,           # safety cap per run
}

COMPARISON_REPORT_PATH = "outputs/comparison_report.txt"