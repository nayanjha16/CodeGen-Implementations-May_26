"""
============================================================
RepoCoder Studio
prompt_builder.py  —  v2.6
============================================================

Task-aware prompt construction for unified multi-task student training.

v2.6 updates
------------
- Keeps the public API used by the current notebook/modules.
- Adds task-specific response headers instead of a generic `### Response`.
- Adds task-specific success criteria to strengthen supervision.
- Adds deterministic prompt hashing for reproducibility checks.
- Keeps task tokens and strict task contracts to reduce task interference.
"""

from __future__ import annotations

import hashlib
from copy import deepcopy
from typing import Any, Dict, List

PROMPT_VERSION = "prompt_contract_v2.6"
TASK_CONTRACT_VERSION = "task_contract_v2.6"


TASK_PROMPT_PROFILES: Dict[str, Dict[str, Any]] = {
    "T1": {
        "task_token": "<TASK_NL_TO_PYTHON>",
        "label": "T1: Natural Language -> Python",
        "source": "Natural Language",
        "target": "Python",
        "task_family": "nl_to_code",
        "instruction": "Generate a correct Python implementation for the programming task.",
        "role": "You are a Python code generator.",
        "objective": "Convert the programming task description into executable Python source code.",
        "output_contract": "Return Python source code only.",
        "response_header": "### Python",
        "constraints": [
            "Do not include Markdown fences.",
            "Do not include explanations or prose.",
            "Do not output Java or pseudocode.",
            "Preserve the intended algorithm and observable behaviour.",
            "Prefer clear functions and executable Python syntax.",
        ],
        "quality_checks": [
            "The output should parse with Python ast.parse.",
            "The output should contain only Python code.",
        ],
        "success_criteria": [
            "Valid Python syntax.",
            "Implements the requested task behaviour.",
            "Contains no markdown or explanatory prose.",
        ],
        "forbidden_outputs": ["markdown", "explanation", "java", "pseudocode"],
        "stop_sequences": ["### Instruction", "### Input", "### Task Contract"],
    },
    "T2": {
        "task_token": "<TASK_NL_TO_JAVA>",
        "label": "T2: Natural Language -> Java",
        "source": "Natural Language",
        "target": "Java",
        "task_family": "nl_to_code",
        "instruction": "Generate a correct Java implementation for the programming task.",
        "role": "You are a Java code generator.",
        "objective": "Convert the programming task description into compilable Java source code.",
        "output_contract": "Return Java source code only.",
        "response_header": "### Java",
        "constraints": [
            "Do not include Markdown fences.",
            "Do not include explanations or prose.",
            "Do not output Python or pseudocode.",
            "Include a compilable class wrapper when required.",
            "Preserve the intended algorithm and observable behaviour.",
        ],
        "quality_checks": [
            "The output should compile with javac after wrapper normalization.",
            "The output should contain only Java code.",
        ],
        "success_criteria": [
            "Compilable Java syntax.",
            "Implements the requested task behaviour.",
            "Contains no markdown or explanatory prose.",
        ],
        "forbidden_outputs": ["markdown", "explanation", "python", "pseudocode"],
        "stop_sequences": ["### Instruction", "### Input", "### Task Contract"],
    },
    "T3": {
        "task_token": "<TASK_PYTHON_TO_JAVA>",
        "label": "T3: Python -> Java",
        "source": "Python",
        "target": "Java",
        "task_family": "code_translation",
        "instruction": "Translate the Python implementation into semantically equivalent Java code.",
        "role": "You are a Python-to-Java translator.",
        "objective": "Preserve the program behaviour while translating the implementation into Java.",
        "output_contract": "Return Java source code only.",
        "response_header": "### Java Translation",
        "constraints": [
            "Do not include Markdown fences.",
            "Do not summarize or explain the code.",
            "Do not output Python.",
            "Preserve the algorithm and observable behaviour.",
            "Preserve asymptotic complexity when possible.",
            "Include a compilable class wrapper when required.",
        ],
        "quality_checks": [
            "The output should compile with javac after wrapper normalization.",
            "The output should solve the same task as the Python input.",
        ],
        "success_criteria": [
            "Compilable Java syntax.",
            "Equivalent observable behaviour to the Python input.",
            "Comparable asymptotic complexity where possible.",
            "Contains no Python, markdown, or explanation.",
        ],
        "forbidden_outputs": ["markdown", "explanation", "python", "summary"],
        "stop_sequences": ["### Instruction", "### Input", "### Task Contract"],
    },
    "T4": {
        "task_token": "<TASK_JAVA_TO_PYTHON>",
        "label": "T4: Java -> Python",
        "source": "Java",
        "target": "Python",
        "task_family": "code_translation",
        "instruction": "Translate the Java implementation into semantically equivalent Python code.",
        "role": "You are a Java-to-Python translator.",
        "objective": "Preserve the program behaviour while translating the implementation into Python.",
        "output_contract": "Return Python source code only.",
        "response_header": "### Python Translation",
        "constraints": [
            "Do not include Markdown fences.",
            "Do not summarize or explain the code.",
            "Do not output Java.",
            "Preserve the algorithm and observable behaviour.",
            "Preserve asymptotic complexity when possible.",
            "Use executable Python syntax.",
        ],
        "quality_checks": [
            "The output should parse with Python ast.parse.",
            "The output should solve the same task as the Java input.",
        ],
        "success_criteria": [
            "Valid Python syntax.",
            "Equivalent observable behaviour to the Java input.",
            "Comparable asymptotic complexity where possible.",
            "Contains no Java, markdown, or explanation.",
        ],
        "forbidden_outputs": ["markdown", "explanation", "java", "summary"],
        "stop_sequences": ["### Instruction", "### Input", "### Task Contract"],
    },
    "T5": {
        "task_token": "<TASK_PYTHON_TO_NL>",
        "label": "T5: Python -> Natural Language",
        "source": "Python",
        "target": "Natural Language",
        "task_family": "code_to_nl",
        "instruction": "Write a concise natural-language programming task description for the Python implementation.",
        "role": "You are a programming task summarizer.",
        "objective": "Describe what the Python program computes as a task specification.",
        "output_contract": "Return natural language only.",
        "response_header": "### Explanation",
        "constraints": [
            "Do not include source code.",
            "Do not include Markdown fences.",
            "Do not rewrite or translate the code.",
            "Focus on purpose, inputs, output, and algorithmic intent.",
            "Keep the description concise and task-oriented.",
        ],
        "quality_checks": [
            "The output should be readable natural language.",
            "The output should not contain code blocks.",
        ],
        "success_criteria": [
            "Clear natural-language task description.",
            "Mentions the program purpose and observable output.",
            "Contains no code or markdown fences.",
        ],
        "forbidden_outputs": ["code", "markdown", "python", "java"],
        "stop_sequences": ["### Instruction", "### Input", "### Task Contract"],
    },
    "T6": {
        "task_token": "<TASK_JAVA_TO_NL>",
        "label": "T6: Java -> Natural Language",
        "source": "Java",
        "target": "Natural Language",
        "task_family": "code_to_nl",
        "instruction": "Write a concise natural-language programming task description for the Java implementation.",
        "role": "You are a programming task summarizer.",
        "objective": "Describe what the Java program computes as a task specification.",
        "output_contract": "Return natural language only.",
        "response_header": "### Explanation",
        "constraints": [
            "Do not include source code.",
            "Do not include Markdown fences.",
            "Do not rewrite or translate the code.",
            "Focus on purpose, inputs, output, and algorithmic intent.",
            "Keep the description concise and task-oriented.",
        ],
        "quality_checks": [
            "The output should be readable natural language.",
            "The output should not contain code blocks.",
        ],
        "success_criteria": [
            "Clear natural-language task description.",
            "Mentions the program purpose and observable output.",
            "Contains no code or markdown fences.",
        ],
        "forbidden_outputs": ["code", "markdown", "python", "java"],
        "stop_sequences": ["### Instruction", "### Input", "### Task Contract"],
    },
}


class PromptBuilder:
    """Builds task-specific training and inference prompts."""

    prompt_version = PROMPT_VERSION
    task_contract_version = TASK_CONTRACT_VERSION

    def task_profile(self, task_id: str) -> Dict[str, Any]:
        if task_id not in TASK_PROMPT_PROFILES:
            raise ValueError(f"Unknown task_id: {task_id}")
        return deepcopy(TASK_PROMPT_PROFILES[task_id])

    def all_profiles(self) -> Dict[str, Dict[str, Any]]:
        return deepcopy(TASK_PROMPT_PROFILES)

    def build_instruction(self, task_id: str) -> str:
        return str(self.task_profile(task_id)["instruction"])

    def response_header(self, task_id: str) -> str:
        return str(self.task_profile(task_id).get("response_header", "### Response"))

    def build_task_contract(self, task_id: str) -> str:
        profile = self.task_profile(task_id)
        constraints = "\n".join(f"- {item}" for item in profile.get("constraints", []))
        quality_checks = "\n".join(f"- {item}" for item in profile.get("quality_checks", []))
        success_criteria = "\n".join(f"- {item}" for item in profile.get("success_criteria", []))
        forbidden = ", ".join(profile.get("forbidden_outputs", []))
        return (
            f"Prompt Version: {PROMPT_VERSION}\n"
            f"Task Token: {profile['task_token']}\n"
            f"Task ID: {task_id}\n"
            f"Task: {profile['label']}\n"
            f"Source Modality: {profile['source']}\n"
            f"Target Modality: {profile['target']}\n"
            f"Role: {profile['role']}\n"
            f"Objective: {profile['objective']}\n"
            f"Output Contract: {profile['output_contract']}\n"
            f"Expected Response Header: {profile.get('response_header', '### Response')}\n"
            f"Forbidden Output Types: {forbidden}\n"
            f"Constraints:\n{constraints}\n"
            f"Quality Checks:\n{quality_checks}\n"
            f"Success Criteria:\n{success_criteria}"
        )

    def build_training_text(
        self,
        instruction: str,
        input_text: str,
        output_text: str,
        task_id: str = "",
    ) -> str:
        """Builds complete supervised fine-tuning text."""
        if not task_id:
            return (
                "### Instruction\n"
                f"{instruction}\n\n"
                "### Input\n"
                f"{input_text}\n\n"
                "### Response\n"
                f"{output_text}"
            )
        profile = self.task_profile(task_id)
        header = profile.get("response_header", "### Response")
        return (
            f"{profile['task_token']}\n"
            "### Task Contract\n"
            f"{self.build_task_contract(task_id)}\n\n"
            "### Instruction\n"
            f"{instruction}\n\n"
            "### Input\n"
            f"{input_text}\n\n"
            f"{header}\n"
            f"{output_text}"
        )

    def build_inference_prompt(
        self,
        instruction: str,
        input_text: str,
        task_id: str = "",
    ) -> str:
        """Builds inference prompt without the reference response."""
        if not task_id:
            return (
                "### Instruction\n"
                f"{instruction}\n\n"
                "### Input\n"
                f"{input_text}\n\n"
                "### Response\n"
            )
        profile = self.task_profile(task_id)
        header = profile.get("response_header", "### Response")
        return (
            f"{profile['task_token']}\n"
            "### Task Contract\n"
            f"{self.build_task_contract(task_id)}\n\n"
            "### Instruction\n"
            f"{instruction}\n\n"
            "### Input\n"
            f"{input_text}\n\n"
            f"{header}\n"
        )

    def prompt_hash(self, text: str) -> str:
        """Returns a deterministic SHA256 hash for one rendered prompt."""
        return hashlib.sha256(str(text).encode("utf-8")).hexdigest()

    def build_training_text_with_hash(
        self,
        instruction: str,
        input_text: str,
        output_text: str,
        task_id: str = "",
    ) -> Dict[str, str]:
        text = self.build_training_text(
            instruction=instruction,
            input_text=input_text,
            output_text=output_text,
            task_id=task_id,
        )
        return {"text": text, "prompt_hash": self.prompt_hash(text)}

    def stop_sequences(self, task_id: str) -> List[str]:
        return list(self.task_profile(task_id).get("stop_sequences", []))
