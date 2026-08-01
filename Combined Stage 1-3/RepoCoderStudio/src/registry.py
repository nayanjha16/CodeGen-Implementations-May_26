"""
============================================================
RepoCoder Studio
registry.py
============================================================

Registry definitions for datasets, tasks, and metrics.

The registry pattern prevents hardcoding dataset/task/metric logic
throughout the notebook.
"""

from dataclasses import dataclass
from typing import Dict, List, Any

from src.config import CONFIG, AppConfig


# ============================================================
# Dataset Registry
# ============================================================

class DatasetRegistry:
    """
    Stores available dataset adapters.

    Current design:
    - XLCoST is mandatory.
    - CodeXGLUE is the secondary evidence source.
    - AVATAR and TransCoder are intentionally removed.
    """

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.datasets = {}

        self.register_defaults()

    def register_defaults(self):
        self.datasets["XLCoST"] = {
            "enabled": self.config.dataset.use_xlcost,
            "role": "primary",
            "source": self.config.dataset.xlcost_dataset_name,
            "python_config": self.config.dataset.xlcost_python_config,
            "java_config": self.config.dataset.xlcost_java_config,
        }

        self.datasets["CodeXGLUE"] = {
            "enabled": self.config.dataset.use_codexglue,
            "role": "second_evidence_source",
            "source": self.config.dataset.codexglue_dataset_name,
            "python_config": self.config.dataset.codexglue_python_config,
            "java_config": self.config.dataset.codexglue_java_config,
        }

    def enabled_datasets(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: info
            for name, info in self.datasets.items()
            if info.get("enabled", False)
        }

    def summary(self) -> Dict[str, Any]:
        return self.datasets


# ============================================================
# Task Registry
# ============================================================

class TaskRegistry:
    """
    Defines the six Combined Stage supervised tasks.
    """

    def __init__(self):
        self.tasks = {
            "T1": {
                "source": "Natural Language",
                "target": "Python",
                "description": "Generate Python code from natural language.",
            },
            "T2": {
                "source": "Natural Language",
                "target": "Java",
                "description": "Generate Java code from natural language.",
            },
            "T3": {
                "source": "Python",
                "target": "Java",
                "description": "Translate Python code to Java.",
            },
            "T4": {
                "source": "Java",
                "target": "Python",
                "description": "Translate Java code to Python.",
            },
            "T5": {
                "source": "Python",
                "target": "Natural Language",
                "description": "Explain Python code in natural language.",
            },
            "T6": {
                "source": "Java",
                "target": "Natural Language",
                "description": "Explain Java code in natural language.",
            },
        }

    def get(self, task_id: str) -> Dict[str, Any]:
        assert task_id in self.tasks, f"Unknown task_id: {task_id}"
        return self.tasks[task_id]

    def all_tasks(self) -> Dict[str, Dict[str, Any]]:
        return self.tasks


# ============================================================
# Metric Registry
# ============================================================

class MetricRegistry:
    """
    Task-aware metric registry.

    The evaluator must select metrics from this registry rather than
    hardcoding a single combined metric table.
    """

    def __init__(self):
        self.metrics = {
            ("Natural Language", "Python"): {
                "primary": ["python_parse_success"],
                "secondary": ["execution_if_feasible", "official_codebleu", "csr_score"],
                "diagnostic": ["codebleu_lite", "failure_category"],
            },
            ("Natural Language", "Java"): {
                "primary": ["java_compile_success"],
                "secondary": ["execution_if_feasible", "official_codebleu", "csr_score"],
                "diagnostic": ["codebleu_lite", "failure_category"],
            },
            ("Python", "Java"): {
                "primary": ["java_compile_success"],
                "secondary": ["official_codebleu", "csr_score"],
                "diagnostic": ["codebleu_lite", "failure_category"],
            },
            ("Java", "Python"): {
                "primary": ["python_parse_success"],
                "secondary": ["official_codebleu", "csr_score"],
                "diagnostic": ["codebleu_lite", "failure_category"],
            },
            ("Python", "Natural Language"): {
                "primary": ["rouge_l"],
                "secondary": ["sacrebleu"],
                "diagnostic": ["semantic_similarity", "failure_category"],
            },
            ("Java", "Natural Language"): {
                "primary": ["rouge_l"],
                "secondary": ["sacrebleu"],
                "diagnostic": ["semantic_similarity", "failure_category"],
            },
        }

    def get_profile(self, source: str, target: str) -> Dict[str, List[str]]:
        return self.metrics.get((source, target), {"primary": [], "secondary": [], "diagnostic": []})

    def get_metrics(self, source: str, target: str) -> List[str]:
        profile = self.get_profile(source, target)
        return profile["primary"] + profile["secondary"] + profile["diagnostic"]

    def summary(self) -> Dict[str, Dict[str, List[str]]]:
        return {
            f"{source} -> {target}": profile
            for (source, target), profile in self.metrics.items()
        }
