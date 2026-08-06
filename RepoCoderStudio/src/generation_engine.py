"""
============================================================
RepoCoder Studio
generation_engine.py  —  v2.5
============================================================

Model loading and deterministic task-aware generation.
"""

from __future__ import annotations

import ast
import json
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

    def _validate_adapter_manifest(self, adapter_dir) -> None:
        """Fail before loading when deployment config and adapter disagree."""

        manifest_path = adapter_dir / "trained_model_manifest.json"
        if not manifest_path.is_file():
            raise FileNotFoundError(f"LoRA adapter manifest not found: {manifest_path}")
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Invalid LoRA adapter manifest: {manifest_path}: {exc}") from exc

        expected = {
            "base_model": self.config.models.student_model_name,
            "prompt_version": self.config.experiment.prompt_version,
            "training_manifest_version": self.config.experiment.training_manifest_version,
        }
        adapter_name = manifest.get("adapter_name")
        if adapter_name is not None and adapter_name != self.config.training.final_adapter_name:
            raise RuntimeError(
                f"Adapter-name mismatch: configured={self.config.training.final_adapter_name!r}, "
                f"manifest={adapter_name!r}"
            )
        for field, configured_value in expected.items():
            manifest_value = manifest.get(field)
            if manifest_value != configured_value:
                raise RuntimeError(
                    f"Adapter manifest mismatch for {field}: "
                    f"configured={configured_value!r}, manifest={manifest_value!r}"
                )
        dataset_name = manifest.get("task_dataset_filename")
        if dataset_name is not None and dataset_name != self.config.training.task_dataset_filename:
            raise RuntimeError(
                "Adapter manifest mismatch for task_dataset_filename: "
                f"configured={self.config.training.task_dataset_filename!r}, "
                f"manifest={dataset_name!r}"
            )

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
            self._validate_adapter_manifest(adapter_dir)
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

    @staticmethod
    def _code_completion_score(text: str, task_id: str) -> int:
        """Rank completions structurally without executing generated code."""

        stripped = (text or "").strip()
        if not stripped:
            return 0
        if task_id in {"T1", "T4"}:
            stripped = _extract_code(stripped, "python")
            try:
                tree = ast.parse(stripped)
            except (SyntaxError, ValueError, TypeError):
                return 0
            implementation_nodes = [
                node
                for node in tree.body
                if not isinstance(node, (ast.Import, ast.ImportFrom))
                and not (
                    isinstance(node, ast.Expr)
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)
                )
            ]
            if any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for node in implementation_nodes):
                return 3000 + min(len(stripped), 999)
            if implementation_nodes:
                return 2000 + min(len(stripped), 999)
            return 1000
        if task_id in {"T2", "T3"}:
            stripped = _extract_code(stripped, "java")
            has_type = bool(re.search(r"\b(?:class|interface|enum|record)\s+[A-Za-z_]", stripped))
            balanced = stripped.count("{") > 0 and stripped.count("{") == stripped.count("}")
            if has_type and balanced:
                return 3000 + min(len(stripped), 999)
            if has_type:
                return 1000
            return 0
        return 3000 + min(len(stripped), 999)

    @staticmethod
    def _drop_last_evidence_block(context: str) -> str:
        """Remove one complete trailing evidence block; never slice its code."""

        matches = list(
            re.finditer(
                r"(?ms)^# BEGIN EVIDENCE.*?^# END EVIDENCE\s*",
                context or "",
            )
        )
        if not matches:
            return ""
        last = matches[-1]
        reduced = (context[: last.start()] + context[last.end() :]).rstrip()
        reduced = re.sub(
            r"(?ms)\n*### (?:Repository Evidence \(untrusted data\)|Validated Example Evidence)\s*$",
            "",
            reduced,
        ).rstrip()
        return reduced if "# BEGIN EVIDENCE" in reduced else ""

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
        def generate_once(minimum_new_tokens: int = 0) -> str:
            generation_kwargs = {
                "max_new_tokens": max_new_tokens,
                "do_sample": False,
                "pad_token_id": tokenizer.eos_token_id,
                "eos_token_id": tokenizer.eos_token_id,
                "repetition_penalty": self.config.models.generation_repetition_penalty,
            }
            if minimum_new_tokens > 0:
                generation_kwargs["min_new_tokens"] = min(
                    minimum_new_tokens, max_new_tokens
                )
            with torch.no_grad():
                output_ids = model.generate(**inputs, **generation_kwargs)
            # Decode only newly generated tokens. Decoding prompt + completion
            # and removing it as text is brittle under tokenizer normalization.
            generated_ids = output_ids[0, prompt_token_count:]
            decoded = tokenizer.decode(
                generated_ids,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False,
            )
            return self.extract_response(decoded, "")

        response = generate_once()
        first_score = self._code_completion_score(response, task_id)
        if task_id in {"T1", "T2", "T3", "T4"} and first_score < 2000:
            LOG.warning(
                "Code generation ended before an implementation was produced; "
                "retrying once with a guarded minimum completion length."
            )
            retry = generate_once(minimum_new_tokens=48)
            if self._code_completion_score(retry, task_id) > first_score:
                response = retry
        return response

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

        # Start with the complete user input and retrieval context. The former
        # implementation always reduced evidence to 25% of the window, even
        # when the complete prompt already fit; that could cut the final lines
        # from the highest-ranked function and induce incorrect continuations.
        fitted_context = retrieved_context
        fitted_input = input_text
        prompt = render(fitted_input, fitted_context)

        # If the prompt truly exceeds the window, remove complete trailing
        # evidence blocks first. Never token-slice evidence or its injection
        # guards. The highest-ranked first block is retained as long as it fits.
        while count(prompt) > maximum and fitted_context:
            fitted_context = self._drop_last_evidence_block(fitted_context)
            prompt = render(fitted_input, fitted_context)

        # Only the user input may be token-trimmed, and only after whole-block
        # evidence reduction was insufficient. The response header is rebuilt
        # after every change and is therefore never truncated.
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
