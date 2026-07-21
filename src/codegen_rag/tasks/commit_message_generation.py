"""Task 1c: Commit message generation — git diff -> concise commit message."""

from __future__ import annotations

from typing import Any

from codegen_rag.tasks.base_task import BaseTask

_MAX_DIFF_CHARS = 3000  # keep prompts within the 512-token context window


class CommitMessageGenerationTask(BaseTask):
    task_name = "commit_message_generation"

    def build_prompt(self, record: dict[str, Any]) -> str:
        diff = record.get("commit_diff") or record.get("diff", "")
        truncated_diff = diff[:_MAX_DIFF_CHARS]
        return f"# Diff:\n{truncated_diff}\n# Write a concise, informative commit message:\n"

    def postprocess(self, raw_completion: str) -> str:
        # A commit message should be a single short line; take the first
        # non-empty line and cap length defensively.
        for line in raw_completion.splitlines():
            stripped = line.strip().lstrip("#").strip()
            if stripped:
                return stripped[:120]
        return raw_completion.strip()[:120]
