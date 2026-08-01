"""Dataset cleaning, prompt-column construction and train/val splitting."""
import random
from typing import Dict, List, Tuple

from datasets import Dataset

from config.config import CFG
from data.dataset import STAGE1_CODE_COL, STAGE1_DOC_COL
from data.prompt_templates import build_stage1_training_text, build_stage2_training_text
from utils.logger import logger


def build_stage1_prompt_dataset(dataset, tokenizer, doc_col: str = STAGE1_DOC_COL, code_col: str = STAGE1_CODE_COL) -> Dataset:
    """Batched preprocessing: build the `prompt` column and drop everything else."""
    eos_token = tokenizer.eos_token or "<|endoftext|>"

    def _batch(batch):
        return {
            "prompt": [
                build_stage1_training_text(doc, code, eos_token)
                for doc, code in zip(batch[doc_col], batch[code_col])
            ]
        }

    logger.info(
        "Building Stage 1 prompt dataset over %d examples ...", len(dataset))
    prompt_dataset = dataset.map(
        _batch, batched=True, remove_columns=dataset.column_names, desc="Building NL->Java prompts")
    logger.info("Stage 1 prompt dataset ready: %d examples.",
                len(prompt_dataset))
    return prompt_dataset


def _is_valid_pair(java_code: str, csharp_code: str) -> bool:
    """Cheap quality filter: non-empty, not trivially short, and 'looks like code'."""
    java_code, csharp_code = java_code.strip(), csharp_code.strip()
    if not java_code or not csharp_code:
        return False
    if len(java_code) < 10 or len(csharp_code) < 10:
        return False
    if not any(tok in java_code for tok in (";", "{", "}")):
        return False
    if not any(tok in csharp_code for tok in (";", "{", "}")):
        return False
    return True


def build_stage2_splits(raw_pairs: Dict[str, List[dict]], seed: int = CFG.SEED) -> Tuple[List[dict], List[dict]]:
    """Clean, de-duplicate, cap, shuffle and split Java/C# pairs into train/val."""
    random.seed(seed)
    all_pairs = [pair for split_pairs in raw_pairs.values()
                 for pair in split_pairs]
    logger.info("Raw Java/C# pairs: %d", len(all_pairs))

    seen = set()
    clean_pairs = []
    for pair in all_pairs:
        if not _is_valid_pair(pair["java"], pair["cs"]):
            continue
        key = (pair["java"].strip(), pair["cs"].strip())
        if key in seen:
            continue
        seen.add(key)
        clean_pairs.append(
            {"java": pair["java"].strip(), "cs": pair["cs"].strip()})

    random.shuffle(clean_pairs)
    logger.info("Clean, de-duplicated pairs: %d", len(clean_pairs))

    clean_pairs = clean_pairs[:CFG.STAGE2_MAX_SAMPLES]
    if len(clean_pairs) < 20:
        raise ValueError(
            f"Too few valid Java/C# pairs ({len(clean_pairs)}) to train Stage 2.")

     val_size = min(max(50, int(0.05 * len(clean_pairs))),
                   max(1, len(clean_pairs) // 5))
    val_pairs = clean_pairs[:val_size]
    train_pairs = clean_pairs[val_size:]
    if not train_pairs:
        raise ValueError("Training split is empty after the validation cut.")

    logger.info("Stage 2 split -> Train: %d | Validation: %d",
                len(train_pairs), len(val_pairs))
    return train_pairs, val_pairs


def pairs_to_text_dataset(pairs: List[dict], eos_token: str) -> Dataset:
    """Build a single-column ("text") HF Dataset ready for SFT training."""
    texts = [build_stage2_training_text(
        pair["java"], pair["cs"], eos_token) for pair in pairs]
    return Dataset.from_dict({"text": texts})
