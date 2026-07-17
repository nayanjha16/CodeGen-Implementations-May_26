"""Prompt templates for Codegen, Fix, Judge, router, and pattern nodes."""

from __future__ import annotations

JUDGE_PROMPT = """### Instruction: Did this program satisfy the user request?
### User request:
{nl_prompt}
### Program stdout:
{stdout}
### Program stderr:
{stderr}
### Exit code: {exit_code}
### Answer with only YES or NO, then one short reason.
### Response:
"""

FIX_PROMPT = """### Instruction: Fix the Python so it satisfies the user request.
### User request:
{nl_prompt}
### Unit: {unit}
### Current Python:
```python
{python_code}
```
### Runtime output / error:
{runtime}
{ast_block}### Response:
```python
"""

PSEUDOCODE_TO_JAVA_PROMPT = """### Instruction: Convert this pseudocode into Java ({unit}-level).
### Pseudocode:
{nl_prompt}
### Response:
```java
"""

PATTERN_JAVA_PROMPT = """### Instruction: Write Java for the design pattern below ({unit}-level).
### Pattern: {pattern}
### Request:
{nl_prompt}
### Response:
```java
"""

ROUTER_HINTS = {
    "nl": "text_to_pl",
    "java": "pl_to_pl",
    "pseudocode": "pseudocode_to_fn",
}


def format_judge_prompt(nl_prompt: str, stdout: str, stderr: str, exit_code: int) -> str:
    return JUDGE_PROMPT.format(
        nl_prompt=nl_prompt.strip(),
        stdout=(stdout or "(empty)").strip(),
        stderr=(stderr or "(empty)").strip(),
        exit_code=exit_code,
    )


def format_fix_prompt(
    nl_prompt: str,
    python_code: str,
    runtime: str,
    unit: str = "function",
    ast_info: str = "",
) -> str:
    ast_block = f"### AST summary:\n{ast_info}\n" if ast_info.strip() else ""
    return FIX_PROMPT.format(
        nl_prompt=nl_prompt.strip(),
        unit=unit,
        python_code=python_code.strip(),
        runtime=(runtime or "(none)").strip(),
        ast_block=ast_block,
    )


def format_pseudocode_to_java(nl_prompt: str, unit: str = "function") -> str:
    return PSEUDOCODE_TO_JAVA_PROMPT.format(nl_prompt=nl_prompt.strip(), unit=unit)


def format_pattern_java(nl_prompt: str, pattern: str, unit: str = "class") -> str:
    return PATTERN_JAVA_PROMPT.format(
        nl_prompt=nl_prompt.strip(),
        pattern=pattern.strip() or "unspecified",
        unit=unit,
    )


def parse_judge_response(text: str) -> tuple[bool, str]:
    """Parse YES/NO from judge model output."""
    cleaned = (text or "").strip()
    upper = cleaned.upper()
    if upper.startswith("YES"):
        reason = cleaned.split("\n", 1)[-1].strip() if "\n" in cleaned else cleaned[3:].strip(" :,-")
        return True, reason or "YES"
    if upper.startswith("NO"):
        reason = cleaned.split("\n", 1)[-1].strip() if "\n" in cleaned else cleaned[2:].strip(" :,-")
        return False, reason or "NO"
    # Fallback heuristics
    if "YES" in upper and "NO" not in upper[:20]:
        return True, cleaned
    return False, cleaned or "NO"
