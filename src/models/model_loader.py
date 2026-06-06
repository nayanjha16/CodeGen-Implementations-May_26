"""Modular CodeGen model loading with GPU/CPU support."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("codegen")


class CodeGenModel:
    """Wrapper for HuggingFace CodeGen models with configurable generation."""

    def __init__(
        self,
        model_name: str = "Salesforce/codegen-350M-multi",
        device: str = "auto",
        max_length: int = 512,
    ):
        self.model_name = model_name
        self.max_length = max_length
        self.device = self._resolve_device(device)
        self.tokenizer = None
        self.model = None
        self._loaded = False

    @staticmethod
    def _resolve_device(device: str) -> str:
        if device != "auto":
            return device
        try:
            import torch

            return "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"

    def load(self) -> None:
        """Load model and tokenizer from HuggingFace."""
        if self._loaded:
            return

        from transformers import AutoModelForCausalLM, AutoTokenizer

        logger.info("Loading model %s on %s", self.model_name, self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        self.model.to(self.device)
        self.model.eval()
        self._loaded = True

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 0.2,
        top_p: float = 0.95,
        num_beams: int = 1,
        do_sample: bool = False,
        decoding_strategy: str = "greedy",
    ) -> str:
        """Generate text from prompt using greedy or beam search decoding."""
        if not self._loaded:
            self.load()

        import torch

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_length,
        ).to(self.device)

        gen_kwargs: dict[str, Any] = {
            "max_new_tokens": max_new_tokens,
            "pad_token_id": self.tokenizer.eos_token_id,
        }

        if decoding_strategy == "beam":
            gen_kwargs.update(
                num_beams=max(num_beams, 2),
                do_sample=False,
                early_stopping=True,
            )
        else:
            gen_kwargs.update(
                do_sample=do_sample,
                temperature=temperature if do_sample else 1.0,
                top_p=top_p if do_sample else 1.0,
            )

        with torch.no_grad():
            outputs = self.model.generate(**inputs, **gen_kwargs)

        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        if generated.startswith(prompt):
            generated = generated[len(prompt) :].strip()
        return generated.strip()


def load_model(
    model_name: str = "Salesforce/codegen-350M-multi",
    device: str = "auto",
    max_length: int = 512,
    eager: bool = False,
) -> CodeGenModel:
    """Factory function to create and optionally load a CodeGen model."""
    model = CodeGenModel(model_name=model_name, device=device, max_length=max_length)
    if eager:
        model.load()
    return model
