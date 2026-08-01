"""General-purpose text/code comparison metrics (BLEU, exact match)."""
import re

import sacrebleu


def normalize_code(code: str) -> str:
    return re.sub(r"\s+", " ", code.strip())


def compute_bleu(predictions, references) -> float:
    return round(sacrebleu.corpus_bleu(predictions, [references]).score, 4)


def compute_exact_match(predictions, references) -> float:
    matches = sum(normalize_code(p) == normalize_code(r)
                  for p, r in zip(predictions, references))
    return round(matches / len(predictions), 4)
