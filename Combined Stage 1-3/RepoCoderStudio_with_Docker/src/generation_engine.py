"""
============================================================
RepoCoder Studio
generation_engine.py  —  v2.4
============================================================

Model loading and deterministic task-aware generation.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Tuple

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

from src.config import CONFIG, AppConfig
from src.prompt_builder import PromptBuilder
from src.logger import LOG


class GenerationEngine:
    """Handles model loading, prompt construction, generation and extraction."""

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.prompt_builder = PromptBuilder()

    def _load_base_model_and_tokenizer(self) -> Tuple[Any, Any]:
        tokenizer = AutoTokenizer.from_pretrained(self.config.models.student_model_name, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"

        model_kwargs: Dict[str, Any] = {"trust_remote_code": True}
        if torch.cuda.is_available():
            model_kwargs["device_map"] = "auto"
        if self.config.models.use_4bit and torch.cuda.is_available():
            model_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )
        elif torch.cuda.is_available():
            model_kwargs["torch_dtype"] = torch.float16

        LOG.info(f"Loading base model: {self.config.models.student_model_name}")
        model = AutoModelForCausalLM.from_pretrained(self.config.models.student_model_name, **model_kwargs)
        model.eval()
        if hasattr(model, "generation_config"):
            model.generation_config.do_sample = False
            model.generation_config.temperature = None
            model.generation_config.top_p = None
            model.generation_config.top_k = None
        return model, tokenizer

    def load_model(self, model_type: str) -> Tuple[Any, Any]:
        assert model_type in {"baseline", "finetuned"}
        model, tokenizer = self._load_base_model_and_tokenizer()
        if model_type == "finetuned":
            adapter_dir = self.config.storage.project_root() / self.config.storage.adapters_dir / self.config.training.final_adapter_name
            if not adapter_dir.exists():
                raise FileNotFoundError(f"LoRA adapter not found: {adapter_dir}")
            LOG.info(f"Loading LoRA adapter from {adapter_dir}")
            model = PeftModel.from_pretrained(model, str(adapter_dir))
            model.eval()
        return model, tokenizer

    def extract_response(self, decoded: str, prompt: str) -> str:
        text = decoded or ""
        if text.startswith(prompt):
            text = text[len(prompt):]
        if "### Response" in text:
            text = text.split("### Response", 1)[-1]
        for marker in ["### Task Contract", "### Instruction", "### Input", "<|im_end|>", "<|endoftext|>"]:
            if marker in text:
                text = text.split(marker, 1)[0]
        return text.strip()

    def extract_code(self, prediction: str, language: str) -> str:
        text = prediction or ""
        fence = re.search(r"```(?:python|py|java)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
        if fence:
            text = fence.group(1).strip()
        # Remove common chat preambles and trailing explanations.
        text = re.sub(r"^(Here is|Sure, here is|The code is|Below is).*?:", "", text, flags=re.I | re.S).strip()
        if language.lower() == "python":
            # Stop if model starts another section after Python code.
            for marker in ["###", "```", "Explanation:", "Java:"]:
                if marker in text:
                    text = text.split(marker, 1)[0].strip()
        if language.lower() == "java":
            for marker in ["###", "```", "Explanation:", "Python:"]:
                if marker in text:
                    text = text.split(marker, 1)[0].strip()
        return text.strip()

    def generate(self, model, tokenizer, instruction: str, input_text: str, task_id: str = "") -> str:
        prompt = self.prompt_builder.build_inference_prompt(instruction, input_text, task_id=task_id)
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=self.config.models.max_seq_length)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=self.config.models.max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return self.extract_response(decoded, prompt)
