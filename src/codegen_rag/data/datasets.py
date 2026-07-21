"""torch.utils.data.Dataset wrappers for each Checkpoint-1 task."""

from __future__ import annotations

from typing import Any

from torch.utils.data import Dataset

from codegen_rag.data.tokenizer_utils import build_causal_lm_example


class ProgramSynthesisDataset(Dataset):
    """(intent -> code) pairs for program-synthesis fine-tuning/evaluation."""

    def __init__(self, records: list[dict[str, Any]], tokenizer: Any, max_length: int = 512):
        self.records = [r for r in records if r.get("intent") and r.get("code")]
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        record = self.records[idx]
        prompt = f"# Task: {record['intent']}\n"
        return build_causal_lm_example(prompt, record["code"], self.tokenizer, self.max_length)


class DocumentationDataset(Dataset):
    """(code -> docstring) pairs for documentation-generation fine-tuning/evaluation."""

    def __init__(self, records: list[dict[str, Any]], tokenizer: Any, max_length: int = 512):
        self.records = [r for r in records if r.get("code") and r.get("docstring")]
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        record = self.records[idx]
        prompt = f"{record['code']}\n# Documentation:\n"
        return build_causal_lm_example(prompt, record["docstring"], self.tokenizer, self.max_length)


class CommitMessageDataset(Dataset):
    """(diff -> commit message) pairs."""

    def __init__(self, records: list[dict[str, Any]], tokenizer: Any, max_length: int = 512):
        self.records = [r for r in records if r.get("commit_diff") and r.get("commit_message")]
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        record = self.records[idx]
        prompt = f"# Diff:\n{record['commit_diff']}\n# Commit message:\n"
        return build_causal_lm_example(
            prompt, record["commit_message"], self.tokenizer, self.max_length
        )


class CodeTranslationDataset(Dataset):
    """(source_lang code -> target_lang code) pairs, matched by function name
    within the same CoDocBench source file across language-specific dumps."""

    def __init__(
        self,
        source_records: list[dict[str, Any]],
        target_records: list[dict[str, Any]],
        tokenizer: Any,
        source_lang: str,
        target_lang: str,
        max_length: int = 512,
    ):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.pairs = self._align(source_records, target_records)

    @staticmethod
    def _align(
        source_records: list[dict[str, Any]], target_records: list[dict[str, Any]]
    ) -> list[tuple[dict[str, Any], dict[str, Any]]]:
        by_name: dict[str, dict[str, Any]] = {
            r["function_name"]: r for r in target_records if r.get("function_name")
        }
        pairs = []
        for src in source_records:
            name = src.get("function_name")
            if name and name in by_name:
                pairs.append((src, by_name[name]))
        return pairs

    def __len__(self) -> int:
        return len(self.pairs)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        src, tgt = self.pairs[idx]
        prompt = (
            f"# Translate the following {self.source_lang} function to {self.target_lang}:\n"
            f"{src['code']}\n# {self.target_lang} version:\n"
        )
        return build_causal_lm_example(prompt, tgt["code"], self.tokenizer, self.max_length)


class RustFineTuneDataset(Dataset):
    """Plain next-token-prediction dataset over raw Rust (+ anti-forgetting) source."""

    def __init__(self, samples: list[dict[str, Any]], tokenizer: Any, max_length: int = 512):
        self.samples = [s for s in samples if s.get("code")]
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        code = self.samples[idx]["code"]
        encoded = self.tokenizer(
            code,
            max_length=self.max_length,
            truncation=True,
            padding="max_length",
            return_tensors=None,
        )
        import torch

        input_ids = encoded["input_ids"]
        labels = [
            tok if tok != self.tokenizer.pad_token_id else -100 for tok in input_ids
        ]
        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "attention_mask": torch.tensor(encoded["attention_mask"], dtype=torch.long),
            "labels": torch.tensor(labels, dtype=torch.long),
        }
