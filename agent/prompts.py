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
The output must be valid Python that passes ast.parse (no markdown fences in the body).
Fix incomplete expressions: every operator (+, -, *, /, etc.) needs operands on both sides.
Do not only add closing parentheses — restore the intended computation.
For runtime errors: preserve the program's intent and structure (functions, classes, and main flow).
Use the traceback to fix the failing line or its root cause — do not delete statements, calls, or tests just to silence the error.
Prefer guards, validation, correct names/keys/indices, initialization, and exception handling over removing code.
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

# Design patterns the router can recognize/extract from a free-form request.
KNOWN_PATTERNS = (
    "singleton",
    "factory",
    "abstract factory",
    "builder",
    "prototype",
    "adapter",
    "bridge",
    "composite",
    "decorator",
    "facade",
    "flyweight",
    "proxy",
    "chain of responsibility",
    "command",
    "interpreter",
    "iterator",
    "mediator",
    "memento",
    "observer",
    "state",
    "strategy",
    "template method",
    "visitor",
)

ROUTE_CLASSIFY_PROMPT = """### Instruction: Classify the input below into exactly one category.
### Categories:
- nl: a natural-language description of a program to write
- pseudocode: step-by-step algorithm-style text (begin/end, loops written out)
- pattern: a request to implement a named software design pattern
- java: raw Java source code to translate
### Input:
{text}
### Answer with only one word (nl, pseudocode, pattern, or java). If pattern, add the pattern name after a comma.
### Response:
"""


def format_route_prompt(text: str) -> str:
    return ROUTE_CLASSIFY_PROMPT.format(text=(text or "").strip()[:2000])


def parse_route_response(text: str) -> tuple[str, str]:
    """Parse the LLM route classifier output into (input_type, pattern_name).

    Returns one of ``nl | pseudocode | pattern | java`` and, for the pattern
    label, an optional extracted pattern name (else ``""``).
    """
    cleaned = (text or "").strip().lower()
    if not cleaned:
        return "nl", ""
    # Take the first non-empty line, split off an optional pattern name.
    first = cleaned.split("\n", 1)[0].strip()
    label, _, rest = first.partition(",")
    label = label.strip(" .:-\t")
    pattern_name = rest.strip(" .:-\t")

    if label.startswith("pseudo"):
        return "pseudocode", ""
    if label.startswith("java"):
        return "java", ""
    if label.startswith("pattern"):
        name = pattern_name or _first_known_pattern(cleaned)
        return "pattern", name
    if label.startswith("nl"):
        return "nl", ""
    # Fallback: scan the whole response for any signal.
    name = _first_known_pattern(cleaned)
    if name:
        return "pattern", name
    if "pseudo" in cleaned:
        return "pseudocode", ""
    if "java" in cleaned:
        return "java", ""
    return "nl", ""


def _first_known_pattern(text: str) -> str:
    """Return the first KNOWN_PATTERNS name mentioned in ``text`` (or "")."""
    lower = (text or "").lower()
    # Prefer longer names first so "abstract factory" wins over "factory".
    for name in sorted(KNOWN_PATTERNS, key=len, reverse=True):
        if name in lower:
            return name.title()
    return ""


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
