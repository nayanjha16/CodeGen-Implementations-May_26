"""Translator backends behind a single factory."""

from __future__ import annotations

from rustgen.config import Config
from rustgen.translator.base import TranslationTask, Translator
from rustgen.translator.mock import MockTranslator

__all__ = ["MockTranslator", "TranslationTask", "Translator", "get_translator"]


def get_translator(config: Config) -> Translator:
    if config.backend == "mock":
        return MockTranslator()
    if config.backend == "hf":
        from rustgen.translator.hf import HFTranslator

        return HFTranslator(config)
    raise ValueError(f"Unknown backend: {config.backend!r} (expected 'mock' or 'hf')")
