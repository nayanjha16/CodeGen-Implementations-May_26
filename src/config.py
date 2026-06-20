import torch

# =====================================================================
# STAGE 1 & STAGE 2 BASELINE CONFIGURATION
# =====================================================================
MODEL_ID = "Salesforce/codegen-350M-multi"
OUTPUT_PATH = "outputs/zero_shot_predictions.json"


# =====================================================================
# STAGE 3 FINE-TUNING CONFIGURATION
# =====================================================================
STAGE3_MODEL_ID = "Salesforce/codegen-350M-mono"
STAGE3_CHECKPOINT_PATH = "./codegen_lora_sql_checkpoints/results/codegen_lora_sql/checkpoint-1314"
STAGE3_OUTPUT_PATH = "outputs/stage3_lora_predictions.json"


# =====================================================================
# STAGE 4 SCHEMA-GROUNDED EXPERIMENT CONFIGURATION (MATCHED STYLE)
# =====================================================================
STAGE4_MODEL_ID = "Salesforce/codegen-350M-mono"
# 💡 Written exactly like Stage 3 to maintain absolute structural alignment:
STAGE4_CHECKPOINT_PATH = "./codegen_lora_sql_checkpoints_r16/results/codegen_lora_sql/checkpoint-2190"
STAGE4_OUTPUT_PATH = "outputs/stage4_schema_lora_r16/stage4_schema_lora_predictions.json"

# =====================================================================
# STAGE 4 SCHEMA-GROUNDED EXPERIMENT CONFIGURATION (MATCHED STYLE) - TRY3
# =====================================================================
STAGE4_MODEL_ID = "Salesforce/codegen-350M-mono"
# 💡 Written exactly like Stage 3 to maintain absolute structural alignment:
STAGE4_TRY3_CHECKPOINT_PATH = "./stage4_model_weights_checkpoint_2190"
STAGE4_TRY3_OUTPUT_PATH = "outputs/stage4_schema_lora_r16_try3/stage4_schema_lora_predictions.json"

# =====================================================================
# SHARED ENVIRONMENT CONFIGURATIONS
# =====================================================================
DATASET_PATH = "data/spider/dev.json"
TABLES_PATH = "data/spider/tables.json"

MAX_NEW_TOKENS = 150
TEMPERATURE = 0.0  
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"