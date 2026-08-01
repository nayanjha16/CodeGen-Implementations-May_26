"""Independent inference pipeline: NL -> Java -> C#.

Loads already fine-tuned/merged models (never the training code) and exposes
three entry points: Java generation, Java->C# translation, and the full chain.
"""
import re
from typing import Dict

import torch

from config.config import CFG
from data.prompt_templates import (
    STAGE1_RESPONSE_MARKER,
    STAGE2_RESPONSE_MARKER,
    build_stage1_prompt,
    build_stage2_strict_inference_prompt,
)
from models.model_loader import load_finetuned_model
from utils.logger import logger


@torch.inference_mode()
def _run_generation(model, tokenizer, prompt_text: str, max_new_tokens: int) -> str:
    """Greedy decoding primitive shared by generation and evaluation."""
    from unsloth import FastLanguageModel

    FastLanguageModel.for_inference(model)
    inputs = tokenizer(prompt_text, return_tensors="pt").to(model.device)
    output = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id,
    )
    return tokenizer.decode(output[0], skip_special_tokens=True)


def strip_unwanted_csharp_modifiers(csharp_code: str) -> str:
    """Remove C# modifiers that Java->C# translation tends to hallucinate.

    Each removal is only applied when guaranteed not to break compilation:
    'virtual'/'sealed' are always safe to drop; 'override' is dropped only when
    no base class/interface is declared; 'async' is dropped only when there is
    no matching 'await'.
    """
    code = re.sub(r"\bvirtual\s+", "", csharp_code)
    code = re.sub(r"\bsealed\s+", "", code)

    has_inheritance = re.search(
        r"\bclass\s+\w+(<[^>]*>)?\s*:\s*\w", code) is not None
    if not has_inheritance:
        code = re.sub(r"\boverride\s+", "", code)

    if "await" not in code:
        code = re.sub(r"\basync\s+", "", code)

    return code


class CodeGenPipeline:
    """Loads both fine-tuned stages once and exposes NL -> Java -> C# generation."""

    def __init__(self, stage1_repo: str = CFG.HF_REPO, stage2_repo: str = CFG.HF_REPO_STAGE2):
        logger.info("Loading Stage 1 model from '%s' ...", stage1_repo)
        self.stage1_model, self.stage1_tokenizer = load_finetuned_model(
            stage1_repo, CFG.MAX_LENGTH)

        logger.info("Loading Stage 2 model from '%s' ...", stage2_repo)
        self.stage2_model, self.stage2_tokenizer = load_finetuned_model(
            stage2_repo, CFG.STAGE2_MAX_SEQ_LEN)

    def generate_java_from_nl(self, prompt: str, max_new_tokens: int = 300) -> str:
        """Stage 1: natural language -> Java."""
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt must be a non-empty string.")

        full_prompt = build_stage1_prompt(prompt)
        decoded = _run_generation(
            self.stage1_model, self.stage1_tokenizer, full_prompt, max_new_tokens)
        return decoded.split(STAGE1_RESPONSE_MARKER)[-1].strip()

    def generate_csharp_from_java(self, java_code: str, max_new_tokens: int = 400) -> str:
        """Stage 2: Java -> C#."""
        if not isinstance(java_code, str) or not java_code.strip():
            raise ValueError("java_code must be a non-empty string.")

        full_prompt = build_stage2_strict_inference_prompt(java_code)
        decoded = _run_generation(
            self.stage2_model, self.stage2_tokenizer, full_prompt, max_new_tokens)
        generated = decoded.split(STAGE2_RESPONSE_MARKER)[-1].strip()
        return strip_unwanted_csharp_modifiers(generated)

    def generate_csharp_from_nl(
        self, prompt: str, java_max_new_tokens: int = 300, csharp_max_new_tokens: int = 400
    ) -> Dict[str, str]:
        """Full chain: NL -> Java -> C#."""
        java_code = self.generate_java_from_nl(
            prompt, max_new_tokens=java_max_new_tokens)
        csharp_code = self.generate_csharp_from_java(
            java_code, max_new_tokens=csharp_max_new_tokens)
        return {"natural_language": prompt, "java": java_code, "csharp": csharp_code}
