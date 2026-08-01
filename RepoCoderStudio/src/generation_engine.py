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
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from src.code_extraction import extract_code as _extract_code
from src.config import CONFIG, AppConfig
from src.logger import LOG
from src.prompt_builder import PromptBuilder


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
        text = re.sub(
            r"^\s*###\s+(?:Python(?:\s+Translation)?|Java(?:\s+Translation)?|Explanation)\s*\n",
            "",
            text,
            flags=re.IGNORECASE,
        )
        for marker in ["### Task Contract", "### Instruction", "### Input", "<|im_end|>", "<|endoftext|>"]:
            if marker in text:
                text = text.split(marker, 1)[0]
        return text.strip()

    def extract_code(self, prediction: str, language: str) -> str:
        return _extract_code(prediction, language)

    def generate(
        self,
        model,
        tokenizer,
        instruction: str,
        input_text: str,
        task_id: str = "",
        retrieved_context: str = "",
    ) -> str:
        prompt, fitted_input, fitted_context = self._fit_prompt(
            tokenizer,
            instruction,
            input_text,
            task_id,
            retrieved_context,
        )
        if fitted_input != input_text or fitted_context != retrieved_context:
            LOG.warning("Inference prompt was token-budgeted to preserve the task contract and response header.")
        inputs = tokenizer(prompt, return_tensors="pt", truncation=False)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        prompt_token_count = int(inputs["input_ids"].shape[1])
        max_new_tokens = (
            self.config.models.nl_max_new_tokens
            if task_id in {"T5", "T6"}
            else self.config.models.max_new_tokens
        )
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                repetition_penalty=(
                    self.config.models.generation_repetition_penalty
                ),
            )
        # Decode only newly generated tokens. Decoding prompt + completion and
        # then removing the prompt as a string is brittle because tokenizers
        # can normalise whitespace differently on decode.
        generated_ids = output_ids[0, prompt_token_count:]
        decoded = tokenizer.decode(
            generated_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )
        return self.extract_response(decoded, "")

    def _fit_prompt(
        self,
        tokenizer,
        instruction: str,
        input_text: str,
        task_id: str,
        retrieved_context: str,
    ) -> Tuple[str, str, str]:
        """Fit evidence/input while never truncating task headers from the final prompt."""
        maximum = self.config.models.max_seq_length

        def render(current_input: str, current_context: str) -> str:
            if current_context:
                return self.prompt_builder.build_rag_inference_prompt(
                    instruction,
                    current_input,
                    current_context,
                    task_id=task_id,
                )
            return self.prompt_builder.build_inference_prompt(
                instruction,
                current_input,
                task_id=task_id,
            )

        def count(text: str) -> int:
            return len(tokenizer.encode(text, add_special_tokens=True))

        def truncate_tokens(text: str, limit: int) -> str:
            token_ids = tokenizer.encode(text, add_special_tokens=False)
            if len(token_ids) <= limit:
                return text
            return tokenizer.decode(token_ids[: max(1, limit)], skip_special_tokens=True)

        fitted_context = truncate_tokens(retrieved_context, max(32, int(maximum * 0.25)))
        fitted_input = truncate_tokens(input_text, max(64, int(maximum * 0.50)))
        prompt = render(fitted_input, fitted_context)

        # Contract text varies by task/tokenizer. Reduce evidence first, then
        # input, until the complete prompt fits. Never use tokenizer-level
        # right truncation, which would remove the response header.
        while count(prompt) > maximum and fitted_context:
            current = len(tokenizer.encode(fitted_context, add_special_tokens=False))
            fitted_context = truncate_tokens(fitted_context, max(0, current - 32))
            if current <= 32:
                fitted_context = ""
            prompt = render(fitted_input, fitted_context)
        while count(prompt) > maximum and fitted_input:
            current = len(tokenizer.encode(fitted_input, add_special_tokens=False))
            fitted_input = truncate_tokens(fitted_input, max(1, current - 32))
            prompt = render(fitted_input, fitted_context)
            if current <= 1:
                break
        if count(prompt) > maximum:
            raise ValueError(
                "The task contract alone exceeds the configured model context window."
            )
        return prompt, fitted_input, fitted_context
