"""Backward-compatible import path — prefer src.evaluation.ollama_judge.OllamaJudge."""

from src.evaluation.ollama_judge import DEFAULT_JUDGE_MODEL, OllamaJudge

DEFAULT_MODEL = DEFAULT_JUDGE_MODEL
QwenEvaluator = OllamaJudge

__all__ = ["DEFAULT_MODEL", "DEFAULT_JUDGE_MODEL", "OllamaJudge", "QwenEvaluator"]
