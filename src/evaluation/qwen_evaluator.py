"""Backward-compatible import path — prefer src.evaluation.ollama_judge.OllamaJudge."""

from src.evaluation.ollama_judge import OllamaJudge

QwenEvaluator = OllamaJudge

__all__ = ["OllamaJudge", "QwenEvaluator"]
