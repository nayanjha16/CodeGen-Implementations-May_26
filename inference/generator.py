"""Code generation wrapper around fine-tuned checkpoints."""

import os
import re
import sys
from pathlib import Path
from typing import Any, cast

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.device import describe_device, get_best_device, get_inference_dtype

DEFAULT_MODEL = "Salesforce/codegen-350M-multi"
QWEN_DEFAULT_MODEL = "Qwen/Qwen2.5-Coder-0.5B-Instruct"
MULTITASK_MODEL_DIR = "qwen_multitask"


class CodeGenerator:
    def __init__(
        self,
        model_path: str | Path | None = None,
        device: str | None = None,
        max_new_tokens: int = 512,
        temperature: float = 0.2,
        top_p: float = 0.95,
    ):
        self.model_path = str(model_path or DEFAULT_MODEL)
        self.device = get_best_device(device)
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p
        dtype = get_inference_dtype(self.device)

        print(f"Loading generator on {describe_device(self.device)} (dtype={dtype})")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # HF from_pretrained returns a dynamic union the type-checker cannot
        # reconcile with both nn.Module (.to/.eval) and GenerationMixin
        # (.generate); cast to Any to avoid false-positive type errors.
        self.model: Any = cast(
            Any,
            AutoModelForCausalLM.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                torch_dtype=dtype,
            ),
        )
        self.model.to(self.device)
        self.model.eval()

    def generate(
        self,
        prompt: str,
        max_new_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        do_sample: bool | None = None,
        repetition_penalty: float | None = None,
        response_type: str = "code",
    ) -> str:
        # Per-call overrides fall back to instance defaults, preserving
        # the original behaviour when no overrides are supplied.
        max_new_tokens = max_new_tokens or self.max_new_tokens
        temperature = self.temperature if temperature is None else temperature
        top_p = self.top_p if top_p is None else top_p
        do_sample = (temperature > 0) if do_sample is None else do_sample

        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
                repetition_penalty=repetition_penalty or 1.0,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Return only the newly generated portion after the prompt
        if generated.startswith(prompt):
            generated = generated[len(prompt):]
        generated = generated.strip()
        if response_type == "doc":
            return self._extract_documentation(generated)
        return self._extract_code(generated)

    @staticmethod
    def _extract_documentation(text: str) -> str:
        """Extract plain documentation (Code2Doc task)."""
        closing_fence = re.search(r"```", text)
        if closing_fence:
            return text[: closing_fence.start()].strip()
        return text.strip()

    @staticmethod
    def _extract_code(text: str) -> str:
        """Extract the generated Python code.

        The java2py/nl2py prompts end with an OPEN ```python fence, so the
        model's continuation starts with raw code. The real code is therefore
        everything up to the first closing ``` fence; anything after it
        (explanations, extra examples) is hallucinated trailing content that
        must be dropped so it doesn't pollute n-gram metrics.
        """
        # Case 1: continuation of an already-open fence -> code is the prefix
        # before the first closing ```.
        closing = re.search(r"```", text)
        if closing and not re.match(r"\s*```", text):
            return text[: closing.start()].strip()

        # Case 2: a full ```python ... ``` block is present.
        py_match = re.search(r"```python\s*(.*?)```", text, re.DOTALL)
        if py_match:
            return py_match.group(1).strip()

        # Case 3: a full generic ``` ... ``` block is present.
        generic_match = re.search(r"```\s*(.*?)```", text, re.DOTALL)
        if generic_match:
            return generic_match.group(1).strip()

        # Case 4: no fences at all -> whole continuation is the code.
        return text.strip()


def _resolve_model_path(task: str, models_dir: Path) -> tuple[Path | None, str | None]:
    """Return (path, base_model_for_adapter) for a task.

    Prefers the unified multi-task merged checkpoint when present.
    """
    multitask_merged = models_dir / MULTITASK_MODEL_DIR / "merged"
    if multitask_merged.exists():
        return multitask_merged, None

    # Qwen task-specific checkpoints (stage-1 Java2Py uses java2py_qwen/)
    qwen_task_map = {"java2py": "java2py_qwen", "nl2py": "nl2py_qwen"}
    qwen_task = qwen_task_map.get(task, task)
    merged_path = models_dir / qwen_task / "merged"
    if merged_path.exists():
        return merged_path, None

    adapter_path = models_dir / qwen_task / "adapter"
    if adapter_path.exists():
        return adapter_path, QWEN_DEFAULT_MODEL

    # Legacy codegen-350M task dirs
    legacy_merged = models_dir / task / "merged"
    if legacy_merged.exists():
        return legacy_merged, None
    legacy_adapter = models_dir / task / "adapter"
    if legacy_adapter.exists():
        return legacy_adapter, DEFAULT_MODEL

    return None, None


def load_generator(task: str, models_dir: Path | None = None) -> CodeGenerator:
    """Load generator for a given task.

    Supported tasks: nl2py, java2py, code2doc, comments (via multi-task model).

    Set MODEL_ID to a Hugging Face repo id (e.g. username/qwen-multitask) to load
    weights from the Hub instead of the local models/ directory.
    """
    hub_model_id = os.environ.get("MODEL_ID")
    if hub_model_id:
        return CodeGenerator(model_path=hub_model_id)

    models_dir = models_dir or (PROJECT_ROOT / "models")
    model_path, adapter_base = _resolve_model_path(task, models_dir)

    if model_path is not None and adapter_base is None:
        return CodeGenerator(model_path=model_path)

    if model_path is not None and adapter_base is not None:
        base = AutoModelForCausalLM.from_pretrained(
            adapter_base, trust_remote_code=True, torch_dtype="auto"
        )
        model = PeftModel.from_pretrained(base, str(model_path))
        gen = CodeGenerator.__new__(CodeGenerator)
        gen.model_path = str(model_path)
        gen.device = get_best_device()
        gen.max_new_tokens = 512
        gen.temperature = 0.2
        gen.top_p = 0.95
        gen.tokenizer = AutoTokenizer.from_pretrained(str(model_path), trust_remote_code=True)
        if gen.tokenizer.pad_token is None:
            gen.tokenizer.pad_token = gen.tokenizer.eos_token
        gen.model = model.to(gen.device)
        gen.model.eval()
        return gen

    print(f"No fine-tuned model found for {task}, using base model.")
    fallback = QWEN_DEFAULT_MODEL if task in ("java2py", "nl2py", "code2doc", "comments") else DEFAULT_MODEL
    return CodeGenerator(model_path=fallback)
