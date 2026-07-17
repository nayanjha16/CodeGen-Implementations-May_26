"""English→Python drafter for the pivot route (English → Python → Rust).

The translation fine-tune is strongest when the prompt carries a Python
reference (7.1% vs ~1% direct on HumanEval-Rust), so for English→Rust we
first let a general coder model draft the Python, then feed that draft into
the normal translation path. The drafter model is lazy-loaded and entirely
optional — if it can't load or produces unusable code, callers fall back to
direct English→Rust.
"""

from __future__ import annotations

import ast
import re

from rustgen.config import Config

_INSTRUCTION = (
    "Write a single Python function that solves this task. "
    "Reply with only the code, no explanation.\nTask: {description}"
)

_TEST_INSTRUCTION = (
    "A Rust function with this exact signature already exists:\n{signature}\n"
    "It does: {description}\n"
    "Write ONLY a Rust `fn main()` containing 3 `assert_eq!` checks that test "
    "this function with simple inputs. Do NOT define the function itself. "
    "Reply with only the code, no explanation."
)

_SIG_INSTRUCTION = (
    "A Rust function is needed for this task: {description}\n{context}"
    "Write ONLY its Rust function signature — a single line starting with `fn`, "
    "using simple types (isize, i64, u64, f64, bool, &str, String, Vec<isize>). "
    "No body, no braces, no explanation."
)


def extract_python_function(text: str) -> str | None:
    """Pull imports + the first top-level function out of model output.

    Accepts raw code or a fenced ```python block. Returns None when the
    output has no function or does not parse — callers then fall back to
    direct English→Rust rather than feeding garbage to the translator.
    """
    match = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.S)
    code = match.group(1) if match else text
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    kept: list[str] = []
    found_function = False
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            kept.append(ast.get_source_segment(code, node) or "")
        elif isinstance(node, ast.FunctionDef):
            kept.append(ast.get_source_segment(code, node) or "")
            found_function = True
            break
    return "\n".join(kept) if found_function else None


def extract_rust_signature(text: str) -> str | None:
    """Pull a one-line `fn name(args) -> T` signature out of model output."""
    match = re.search(r"```(?:rust)?\s*\n(.*?)```", text, re.S)
    code = match.group(1) if match else text
    for line in code.splitlines():
        line = line.strip()
        if not line.startswith("fn "):
            continue
        line = line.split("{")[0].rstrip(" ;")
        if "(" in line and ")" in line:
            return line
    return None


def extract_rust_main(text: str) -> str | None:
    """Pull ONLY the `fn main() { ... }` block out of model output.

    Anything else the model wrote (its own copy of the solution, prose) is
    discarded, so generated tests can never smuggle in an implementation.
    Returns None when there is no assert-bearing main to be found.
    """
    from rustgen.translator.hf import trim_to_first_fn

    match = re.search(r"```(?:rust)?\s*\n(.*?)```", text, re.S)
    code = match.group(1) if match else text
    start = code.find("fn main")
    if start == -1:
        return None
    block = trim_to_first_fn(code[start:])
    if not block.rstrip().endswith("}") or "assert" not in block:
        return None
    return block


class PythonDrafter:
    """Lazy-loaded coder model that turns an English description into Python."""

    def __init__(self, config: Config):
        self.config = config
        self._model = None
        self._tokenizer = None
        self._device = None

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        if torch.cuda.is_available():
            device, dtype = "cuda", torch.float16
        elif torch.backends.mps.is_available():
            device, dtype = "mps", torch.float16
        else:
            device, dtype = "cpu", torch.float32
        self._device = device
        self._tokenizer = AutoTokenizer.from_pretrained(self.config.pivot_model)
        self._model = AutoModelForCausalLM.from_pretrained(
            self.config.pivot_model, dtype=dtype
        ).to(device)
        self._model.eval()

    def _chat(self, content: str, max_new_tokens: int) -> str:
        self._ensure_loaded()
        import torch

        prompt = self._tokenizer.apply_chat_template(
            [{"role": "user", "content": content}],
            tokenize=False, add_generation_prompt=True,
        )
        inputs = self._tokenizer(prompt, return_tensors="pt").to(self._device)
        with torch.no_grad():
            output = self._model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=self._tokenizer.eos_token_id,
            )
        return self._tokenizer.decode(
            output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True
        )

    def draft(self, description: str, max_new_tokens: int = 300) -> str | None:
        """English description -> Python function source, or None on failure."""
        text = self._chat(_INSTRUCTION.format(description=description), max_new_tokens)
        return extract_python_function(text)

    def draft_signature(self, description: str, python: str | None = None,
                        max_new_tokens: int = 80) -> str | None:
        """English description (+ optional Python) -> one-line Rust signature."""
        context = ""
        if python:
            context = "Reference Python implementation:\n" + python.strip() + "\n"
        text = self._chat(
            _SIG_INSTRUCTION.format(description=description, context=context),
            max_new_tokens,
        )
        return extract_rust_signature(text)

    def draft_tests(self, description: str, signature: str,
                    max_new_tokens: int = 300) -> str | None:
        """English description + Rust signature -> `fn main` with assert_eq!
        checks, or None on failure. Model-generated tests are indicative only —
        the measured benchmark numbers use MultiPL-E's curated suites."""
        from rustgen.rag.prompt import normalize_signature

        sig = normalize_signature(signature).rstrip("{ ").strip()
        text = self._chat(
            _TEST_INSTRUCTION.format(signature=sig, description=description),
            max_new_tokens,
        )
        return extract_rust_main(text)
