"""Single source of truth for every tunable value in the pipeline."""
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Config:
    # --- Reproducibility ---
    SEED: int = 3407

    # --- Base model (shared by both stages) ---
    MODEL_NAME: str = "unsloth/Qwen2.5-Coder-1.5B-Instruct-bnb-4bit"
    MAX_LENGTH: int = 2048

    # --- Stage 1: NL -> Java ---
    DATASET_NAME: str = "code_search_net"
    DATASET_CONFIG: str = "java"
    STAGE1_TRAIN_SAMPLES: int = 5000
    STAGE1_OUTPUT_DIR: str = "./checkpoints/nl2java"

    # --- LoRA (Stage 1) ---
    LORA_R: int = 16
    LORA_ALPHA: int = 32
    LORA_DROPOUT: float = 0.0
    LORA_BIAS: str = "none"
    LORA_TARGET_MODULES: Tuple[str, ...] = (
        "q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj",
    )

    # --- Training (Stage 1) ---
    EPOCHS: int = 3
    BATCH_SIZE: int = 4
    GRAD_ACCUM: int = 4
    LEARNING_RATE: float = 2e-5
    SAVE_STRATEGY: str = "epoch"
    LOGGING_STEPS: int = 20

    # --- Stage 2: Java -> C# ---
    STAGE2_MAX_SEQ_LEN: int = 1024
    STAGE2_MAX_SAMPLES: int = 6000
    STAGE2_EPOCHS: int = 2
    STAGE2_BATCH_SIZE: int = 2
    STAGE2_GRAD_ACCUM: int = 4
    STAGE2_LEARNING_RATE: float = 2e-4
    STAGE2_LORA_ALPHA: int = 16
    STAGE2_OUTPUT_DIR: str = "./checkpoints/java2csharp"

    # --- Evaluation ---
    EVAL_SAMPLES: int = 100
    STAGE2_EVAL_SAMPLES: int = 50

    # --- Output / publishing ---
    SAVE_DIR: str = "./saved_models"
    # Stage 1 and Stage 2 are separate sequential LoRA adapters and cannot be
    # fused into a single merged model, so each is published to its own repo.
    HF_REPO: str = "shibsankardhara2/Qwen2.5-Coder-1.5B-NL-Java_V5"
    HF_REPO_STAGE2: str = "shibsankardhara2/Qwen2.5-Coder-1.5B-Java-CSharp_V5"


CFG = Config()
