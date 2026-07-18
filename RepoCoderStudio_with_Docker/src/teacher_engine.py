"""
============================================================
RepoCoder Studio
teacher_engine.py — v2.3 Batch 2
============================================================

Teacher Engine.

Design role
-----------
Implements the teacher side of the teacher-student architecture for
corpus engineering only. Teacher outputs are never trusted directly;
they are validation candidates that must pass deterministic validators.

Batch 2 changes
---------------
1. Separates teacher repair enablement from teacher test generation.
2. Keeps lazy loading so imports do not consume GPU memory.
3. Uses deterministic generation configuration to avoid sampling warnings.
4. Returns structured metadata for every generation call.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from src.config import CONFIG, AppConfig
from src.logger import LOG


class TeacherEngine:
    """Teacher model wrapper for completion, repair and candidate tests."""

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.model = None
        self.tokenizer = None
        self._load_error: Optional[str] = None

    def _feature_enabled(self, feature: str = "repair") -> bool:
        if feature == "tests":
            return bool(getattr(self.config.validation, "enable_teacher_test_generation", False))
        return bool(getattr(self.config.validation, "enable_teacher_repair", False))

    def _load_model(self, feature: str = "repair") -> bool:
        if self.model is not None and self.tokenizer is not None:
            return True

        if not self._feature_enabled(feature):
            self._load_error = f"teacher_{feature}_disabled_by_config"
            return False

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

            model_name = self.config.models.teacher_model_name
            tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            model_kwargs: Dict[str, Any] = {
                "trust_remote_code": True,
                "device_map": "auto",
            }

            if self.config.models.use_4bit and torch.cuda.is_available():
                model_kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                )
            elif torch.cuda.is_available():
                model_kwargs["torch_dtype"] = torch.float16

            model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
            model.eval()

            if hasattr(model, "generation_config"):
                model.generation_config.do_sample = False
                model.generation_config.temperature = None
                model.generation_config.top_p = None
                model.generation_config.top_k = None

            self.model = model
            self.tokenizer = tokenizer
            LOG.info(f"Teacher model loaded: {model_name}")
            return True

        except Exception as exc:
            self._load_error = repr(exc)
            LOG.warning(f"Teacher model unavailable: {self._load_error}")
            return False

    def _run_generation(self, prompt: str, max_new_tokens: Optional[int] = None, feature: str = "repair") -> Dict[str, Any]:
        if not self._load_model(feature=feature):
            return {
                "status": "UNAVAILABLE",
                "text": "",
                "reason": self._load_error or "teacher_unavailable",
                "teacher_model": self.config.models.teacher_model_name,
            }

        assert self.model is not None
        assert self.tokenizer is not None
        import torch

        max_new_tokens = max_new_tokens or self.config.models.max_new_tokens
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.config.models.max_seq_length,
        )
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        decoded = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        text = decoded[len(prompt):].strip() if decoded.startswith(prompt) else decoded.strip()
        for marker in ["### Instruction", "### Input", "<|im_end|>", "<|endoftext|>"]:
            if marker in text:
                text = text.split(marker, 1)[0].strip()

        return {
            "status": "PASS",
            "text": text.strip(),
            "teacher_model": self.config.models.teacher_model_name,
            "max_new_tokens": max_new_tokens,
        }

    def _extract_fenced_or_plain_code(self, text: str) -> str:
        fence = re.search(r"```(?:python|py|java)?\s*(.*?)```", text or "", flags=re.I | re.S)
        if fence:
            return fence.group(1).strip()
        return (text or "").strip()

    def generate_natural_language(self, python_code: str, java_code: str, feedback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        prompt = f"""### Instruction
Write one concise programming-task description that accurately describes the behavior of the given Python and Java implementations.

Rules:
- Return only natural language.
- Do not include source code.
- Do not mention Python or Java.
- Describe the task, input behavior, and output behavior.

### Python
{python_code}

### Java
{java_code}

### Validation Feedback
{json.dumps(feedback or {}, ensure_ascii=False)}

### Response
"""
        result = self._run_generation(prompt, max_new_tokens=160, feature="repair")
        if result["status"] != "PASS":
            return {
                **result,
                "text": "Compute the result implemented by the provided program.",
                "fallback_used": True,
            }
        return result

    def generate_python(self, natural_language: str, java_code: str, feedback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        prompt = f"""### Instruction
Generate a correct Python implementation for the programming task.

Rules:
- Return only Python source code.
- Do not include explanation.
- Preserve the behavior described by the task and Java reference.

### Task
{natural_language}

### Java Reference
{java_code}

### Validation Feedback
{json.dumps(feedback or {}, ensure_ascii=False)}

### Response
"""
        result = self._run_generation(prompt, feature="repair")
        result["text"] = self._extract_fenced_or_plain_code(result.get("text", ""))
        return result

    def generate_java(self, natural_language: str, python_code: str, feedback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        prompt = f"""### Instruction
Generate a correct Java implementation for the programming task.

Rules:
- Return only Java source code.
- Include a compilable class wrapper when needed.
- Do not include explanation.
- Preserve the behavior described by the task and Python reference.

### Task
{natural_language}

### Python Reference
{python_code}

### Validation Feedback
{json.dumps(feedback or {}, ensure_ascii=False)}

### Response
"""
        result = self._run_generation(prompt, feature="repair")
        result["text"] = self._extract_fenced_or_plain_code(result.get("text", ""))
        return result

    def propose_tests(self, natural_language: str, python_code: str, java_code: str) -> Dict[str, Any]:
        prompt = f"""### Instruction
Propose up to 3 simple logical tests for the programming task.

Rules:
- Return JSON only.
- Return a list of objects.
- Each object should contain input and expected_output.
- Do not include Python or Java test code.

### Task
{natural_language}

### Python
{python_code}

### Java
{java_code}

### Response
"""
        result = self._run_generation(prompt, max_new_tokens=256, feature="tests")
        text = result.get("text", "")
        tests: List[Dict[str, Any]] = []
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                tests = [x for x in parsed if isinstance(x, dict)]
            elif isinstance(parsed, dict):
                raw_tests = parsed.get("tests", [])
                tests = [x for x in raw_tests if isinstance(x, dict)]
        except Exception:
            tests = []
        return {
            **result,
            "candidate_tests": tests,
            "status": "PASS" if tests else "INSUFFICIENT",
        }
