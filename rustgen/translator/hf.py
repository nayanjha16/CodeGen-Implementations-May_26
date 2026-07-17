"""HuggingFace backend: codegen-350M(-derived) base + optional LoRA adapter.

transformers/peft/torch are imported lazily inside the class so the mock
path never needs them installed.
"""

from __future__ import annotations

from rustgen.config import Config
from rustgen.rag.prompt import build_prompt, normalize_signature
from rustgen.translator.base import TranslationTask, Translator


class HFTranslator(Translator):
    def __init__(self, config: Config):
        self.config = config
        self._model = None
        self._tokenizer = None
        self._device = None

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            raise ImportError(
                "The 'hf' backend needs the ML extras: pip install -e '.[ml]'"
            ) from exc

        device = self.config.device
        if device == "auto":
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
        self._device = device

        self._tokenizer = AutoTokenizer.from_pretrained(self.config.base_model)
        model = AutoModelForCausalLM.from_pretrained(self.config.base_model)
        if self.config.adapter_path:
            from peft import PeftModel

            model = PeftModel.from_pretrained(model, self.config.adapter_path)
        model.to(device)
        model.eval()
        self._model = model

    def generate(self, task: TranslationTask) -> str:
        self._ensure_loaded()
        import torch

        prompt = build_prompt(task, task.context_examples)
        inputs = self._tokenizer(prompt, return_tensors="pt").to(self._device)
        with torch.no_grad():
            output = self._model.generate(
                **inputs,
                max_new_tokens=self.config.max_new_tokens,
                do_sample=False,
                pad_token_id=self._tokenizer.eos_token_id,
            )
        new_tokens = output[0][inputs["input_ids"].shape[1]:]
        completion = self._tokenizer.decode(new_tokens, skip_special_tokens=True)

        if task.signature:
            # The prompt ended with `fn sig(...) {`, so the model wrote a body.
            body = trim_to_body(completion)
            if not body.endswith("\n"):
                body += "\n"
            return normalize_signature(task.signature) + "\n" + body + "}"
        return trim_to_first_fn(completion)


def _scan_to_close(code: str, depth: int) -> int | None:
    """Index of the brace that brings ``depth`` to 0, ignoring braces inside
    strings, char literals, and comments. None if it never closes."""
    i, n = 0, len(code)
    in_str = in_char = in_line = in_block = False
    opened = depth > 0
    while i < n:
        ch = code[i]
        nxt = code[i + 1] if i + 1 < n else ""
        if in_line:
            if ch == "\n":
                in_line = False
            i += 1
            continue
        if in_block:
            if ch == "*" and nxt == "/":
                in_block = False
                i += 2
                continue
            i += 1
            continue
        if in_str:
            if ch == "\\":
                i += 2
                continue
            if ch == '"':
                in_str = False
            i += 1
            continue
        if in_char:
            if ch == "\\":
                i += 2
                continue
            if ch == "'":
                in_char = False
            i += 1
            continue
        if ch == "/" and nxt == "/":
            in_line = True
            i += 2
            continue
        if ch == "/" and nxt == "*":
            in_block = True
            i += 2
            continue
        if ch == '"':
            in_str = True
            i += 1
            continue
        if ch == "'":
            # lifetime ('a) vs char literal ('x' or '\n')
            if nxt == "\\" or (i + 2 < n and code[i + 2] == "'"):
                in_char = True
            i += 1
            continue
        if ch == "{":
            depth += 1
            opened = True
        elif ch == "}":
            depth -= 1
            if opened and depth == 0:
                return i
        i += 1
    return None


def trim_to_body(text: str) -> str:
    """Generation continued after ``fn sig(...) {`` — cut just before the brace
    that closes the function (the notebooks' fixed ``trim_to_body``)."""
    close = _scan_to_close(text, depth=1)
    return text if close is None else text[:close]


def trim_to_first_fn(code: str) -> str:
    """Cut generated text down to the first brace-balanced function."""
    close = _scan_to_close(code, depth=0)
    return code if close is None else code[: close + 1]
