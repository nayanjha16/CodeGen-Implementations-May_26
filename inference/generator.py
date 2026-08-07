"""Code generation wrapper around fine-tuned checkpoints."""

import ast
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
from utils.text_sanitize import truncate_roleplay_continuation

DEFAULT_MODEL = "Salesforce/codegen-350M-multi"
QWEN_DEFAULT_MODEL = "Qwen/Qwen2.5-Coder-0.5B-Instruct"
MULTITASK_MODEL_DIR = "qwen_multitask"
# Same fine-tuned weights as local models/qwen_multitask/merged (uploaded to Hub).
HF_FT_MODEL = "Saikrishna2511/qwen-multitask"
# Gradio Space UI only — loads HF_FT_MODEL via Space MODEL_ID.
HF_SPACE_ID = "Saikrishna2511/qwen-multitask-demo"


def local_merged_path(models_dir: Path | None = None) -> Path:
    """Path to the local multitask merged checkpoint."""
    root = models_dir or (PROJECT_ROOT / "models")
    return root / MULTITASK_MODEL_DIR / "merged"


def resolve_codegen_model_id(
    *,
    explicit: str | None = None,
    models_dir: Path | None = None,
) -> str:
    """Resolve FT codegen model: MODEL_ID env → local merged → Hub FT repo.

    Local ``models/qwen_multitask/merged`` and ``Saikrishna2511/qwen-multitask``
    are the same fine-tuned weights. Never falls back to base Qwen here.
    """
    if explicit and str(explicit).strip():
        return str(explicit).strip()
    env_id = (os.environ.get("MODEL_ID") or "").strip()
    if env_id:
        return env_id
    merged = local_merged_path(models_dir)
    if merged.exists():
        return str(merged.resolve())
    return HF_FT_MODEL


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

        max_input_length = 3072 if response_type == "doc" else 1024
        inputs = self.tokenizer(
            prompt, return_tensors="pt", truncation=True, max_length=max_input_length
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        input_len = inputs["input_ids"].shape[1]

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

        generated = self.tokenizer.decode(
            outputs[0][input_len:], skip_special_tokens=True
        ).strip()
        if response_type == "doc":
            return self._extract_documentation(generated)
        return self._extract_code(generated)

    @staticmethod
    def _extract_documentation(text: str) -> str:
        """Extract plain documentation (Code2Doc task)."""
        raw = truncate_roleplay_continuation(text)
        if not raw:
            return ""
        closing_fence = re.search(r"\n```", raw)
        if closing_fence:
            return raw[: closing_fence.start()].strip()
        return raw

    @staticmethod
    def _extract_code(text: str) -> str:
        """Extract the generated Python code.

        The java2py/nl2py prompts end with an OPEN ```python fence, so the
        model's continuation starts with raw code and stops at the first closing
        fence; anything after it (explanations, extra examples) is hallucinated
        trailing content that must be dropped so it doesn't pollute n-gram
        metrics. Leading prose, missing closing fences and stray language tags
        are also handled so leftover markdown never reaches the AST/sandbox.
        """
        raw = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
        if not raw:
            return ""

        first = raw.find("```")

        # Case 1: continuation of an already-open fence -> code is the prefix
        # before the first closing ```. Trust it only when it really is Python.
        if first > 0:
            prefix = raw[:first].strip()
            if prefix and _is_probably_python(prefix):
                return _strip_language_tag(prefix)

        # Case 2: a complete ```lang ... ``` block, skipping any leading prose.
        block = re.search(r"```[ \t]*\w*[ \t]*\n(.*?)```", raw, re.DOTALL)
        if block:
            return _strip_language_tag(block.group(1).strip())

        # Case 3: an unclosed opening fence -> drop the fence line, keep the rest.
        opening = re.search(r"```[ \t]*\w*[ \t]*\n", raw)
        if opening:
            return _strip_language_tag(raw[opening.end():].split("```")[0].strip())

        # Case 4: a fence with nothing usable after it.
        if first > 0:
            return _strip_language_tag(raw[:first].strip())
        if first == 0:
            return _strip_language_tag(raw.lstrip("`").strip())

        # Case 5: no fences at all -> whole continuation is the code.
        return _strip_language_tag(raw)


def _is_probably_python(text: str) -> bool:
    """Distinguish real Python from prose/markdown left in the model output."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return False
    body = getattr(tree, "body", [])
    if not body:
        return False
    # A lone bare name/literal ("Sure", "python") is prose, not code.
    if len(body) == 1 and isinstance(body[0], ast.Expr):
        if isinstance(body[0].value, (ast.Name, ast.Constant)):
            return False
    return True


def _strip_language_tag(code: str) -> str:
    """Drop a stray leading ``python``/``py``/``java`` line echoed by the model."""
    parts = code.split("\n", 1)
    if len(parts) > 1 and parts[0].strip().lower() in ("python", "py", "java"):
        return parts[1].strip()
    return code


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

    Resolution: ``MODEL_ID`` env → local multitask/task checkpoint → Hub FT
    model ``Saikrishna2511/qwen-multitask`` (same weights as local merged).
    """
    env_model_id = (os.environ.get("MODEL_ID") or "").strip()
    if env_model_id:
        return CodeGenerator(model_path=env_model_id)

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

    print(f"Loading fine-tuned Hub model {HF_FT_MODEL}")
    return CodeGenerator(model_path=HF_FT_MODEL)
