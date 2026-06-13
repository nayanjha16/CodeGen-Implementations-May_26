"""RustGen: English/Python -> Rust translation with a swappable model backend."""

from rustgen.config import Config
from rustgen.translator import get_translator
from rustgen.translator.base import TranslationTask, Translator

__version__ = "0.1.0"

__all__ = ["Config", "TranslationTask", "Translator", "get_translator"]
