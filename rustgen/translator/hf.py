"""HuggingFace backend: codegen-350M-multi + optional LoRA adapter.

transformers/peft/torch are imported lazily inside the class so the mock
path never needs them installed.
"""

from __future__ import annotations

from rustgen.config import Config
from rustgen.rag.prompt import build_prompt
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
            device = "cuda" if torch.cuda.is_available() else "cpu"
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
            completion = task.signature.rstrip() + completion
        return trim_to_first_fn(completion)


def trim_to_first_fn(code: str) -> str:
    """Cut generated text down to the first brace-balanced function."""
    depth = 0
    opened = False
    for i, char in enumerate(code):
        if char == "{":
            depth += 1
            opened = True
        elif char == "}":
            depth -= 1
            if opened and depth == 0:
                return code[: i + 1]
    return code
