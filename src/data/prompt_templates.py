"""Prompt templates shared verbatim between training and inference.

Using the exact same builder functions for both keeps the SFT training format
and the inference-time format from ever drifting apart.
"""

STAGE1_RESPONSE_MARKER = "### Response:\n\n"
STAGE1_LANG_HINT = " Write the solution in Java."

STAGE2_INSTRUCTION = "Translate the following Java code into equivalent C#."
STAGE2_RESPONSE_MARKER = "### Response\n"
STAGE2_LANG_HINT = " Write the solution in C#."

STAGE2_INFERENCE_GUARDRAILS = (
    " This is a literal, line-by-line translation task, not a code review: keep "
    "the exact same method name(s), return type(s), parameter names, parameter "
    "types, parameter order, and access modifiers as the Java input. Preserve the "
    "exact algorithm, all loops, conditions, recursion, numeric types, and "
    "exception handling exactly as written in the Java - do not fix bugs, "
    "optimize, simplify, or rewrite the logic, and do not introduce new helper "
    "methods. Only add 'virtual', 'override', 'async', 'sealed', or 'new' "
    "modifiers if the Java input's own modifiers or class hierarchy already "
    "require them; otherwise omit them."
)


def add_java_hint(instruction: str) -> str:
    instruction = instruction.strip()
    if "java" in instruction.lower():
        return instruction
    return f"{instruction}{STAGE1_LANG_HINT}"


def clean_instruction(doc: str) -> str:
    """Extract the human-readable instruction from a javadoc string."""
    return doc.split("@param")[0].strip()


def build_stage1_prompt(instruction: str) -> str:
    """Prompt up to (and including) the response marker - used at inference time."""
    return f"### Instruction:\n\n{add_java_hint(instruction)}\n\n{STAGE1_RESPONSE_MARKER}"


def build_stage1_training_text(doc: str, code: str, eos_token: str) -> str:
    """Full prompt + target Java code + EOS - used for SFT training."""
    return build_stage1_prompt(clean_instruction(doc)) + code + eos_token


def add_csharp_hint(instruction: str) -> str:
    instruction = instruction.strip()
    lowered = instruction.lower()
    if "c#" in lowered or "csharp" in lowered:
        return instruction
    return f"{instruction}{STAGE2_LANG_HINT}"


def build_stage2_inference_prompt(java_code: str) -> str:
    """Prompt up to (and including) the response marker - used at inference time."""
    return (
        "### Instruction\n"
        f"{add_csharp_hint(STAGE2_INSTRUCTION)}\n\n"
        "### Java\n"
        f"{java_code.strip()}\n\n"
        "### Response\n"
    )


def build_stage2_strict_inference_prompt(java_code: str) -> str:
    """Inference-only prompt: base prompt with the guardrail text spliced in
    right before the "### Java" section. Never used for training."""
    base_prompt = build_stage2_inference_prompt(java_code)
    marker = "\n\n### Java\n"
    idx = base_prompt.index(marker)
    return base_prompt[:idx] + STAGE2_INFERENCE_GUARDRAILS + base_prompt[idx:]


def build_stage2_training_text(java_code: str, csharp_code: str, eos_token: str) -> str:
    """Full prompt + target C# code + EOS - used for SFT training."""
    return build_stage2_inference_prompt(java_code) + csharp_code.strip() + eos_token
