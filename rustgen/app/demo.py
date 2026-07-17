"""Gradio demo. Launch with: python -m rustgen.app.demo

One pipeline, one form: give an English description, optionally paste Python
(leave the box empty and the Qwen drafter writes it), and the fine-tuned
350M model produces Rust that rustc then verifies. The route actually taken
(pasted Python / drafted Python / direct) is displayed with every answer.
"""

from __future__ import annotations

import os
import shutil

import gradio as gr

# rustc lives in ~/.cargo/bin; make sure verification finds it even when the
# demo is launched from a shell that hasn't sourced the cargo env.
_CARGO_BIN = os.path.expanduser("~/.cargo/bin")
if os.path.isdir(_CARGO_BIN) and _CARGO_BIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _CARGO_BIN + os.pathsep + os.environ.get("PATH", "")

from rustgen.config import Config
from rustgen.eval.harness import run_rust
from rustgen.rag import get_retriever
from rustgen.translator import get_translator
from rustgen.translator.base import TranslationTask
from rustgen.translator.pivot import PythonDrafter

CONFIG = Config.from_env()
TRANSLATOR = get_translator(CONFIG)
RETRIEVER = get_retriever(CONFIG)
DRAFTER = PythonDrafter(CONFIG)   # lazy: weights load on first pivot use

# gradio's gr.Code has no Rust grammar (as of 6.x); fall back to plain text
RUST_LANG = "rust" if "rust" in gr.Code.languages else None

GENERIC_DESCRIPTION = "Translate the reference Python implementation to Rust."

_CSS = """
#rg-header {display:flex; align-items:center; gap:18px; margin:6px 0 2px;}
#rg-header .rg-logo {width:64px; height:64px; background:#fff; border-radius:14px;
                     padding:7px; box-shadow:0 1px 4px rgba(0,0,0,.18); flex:none;}
#rg-header h1 {margin:0 0 2px; font-size:1.9rem; font-weight:800; letter-spacing:-.02em;}
#rg-header .rg-tag {margin:0; font-size:1rem; line-height:1.45;
                    color:var(--body-text-color-subdued);}
#rg-header .rg-badges {margin-top:7px; display:flex; gap:8px; flex-wrap:wrap;}
#rg-header .rg-badges span {font-size:.72rem; font-weight:600;
                            padding:3px 10px; border-radius:999px;
                            border:1px solid var(--border-color-primary);
                            color:var(--body-text-color-subdued);}
#rg-header .rg-badges span.rg-hot {border-color:#ce422b; color:#ce422b;}
/* compact examples table: small cells, clamped code previews, scroll in place */
#rg-examples table {font-size:.78rem; line-height:1.3;}
#rg-examples td, #rg-examples th {padding:4px 10px !important; vertical-align:top;}
#rg-examples th {white-space:normal !important; overflow-wrap:break-word;
    word-break:normal; max-width:180px; font-size:.72rem;}
#rg-examples td pre, #rg-examples td code {font-size:.7rem !important; line-height:1.25;
    max-height:3.2em; overflow:hidden; margin:0;}
#rg-examples .table-wrap, #rg-examples > div {max-height:230px; overflow:auto;}
"""


def _header_html() -> str:
    import base64
    from pathlib import Path

    logo_tag = ""
    logo_path = Path(__file__).parent / "assets" / "rust-logo.svg"
    if logo_path.exists():
        encoded = base64.b64encode(logo_path.read_bytes()).decode()
        logo_tag = (f'<img class="rg-logo" alt="Rust" '
                    f'src="data:image/svg+xml;base64,{encoded}"/>')
    return f"""
<div id="rg-header">
  {logo_tag}
  <div>
    <h1>RustGen</h1>
    <p class="rg-tag">English or Python in — execution-verified Rust out.
    One pipeline: <em>(optional) Qwen drafts the Python</em> → our Rust-fine-tuned
    codegen-350M translates → <code>rustc</code> verifies.</p>
    <div class="rg-badges">
      <span>HumanEval-Rust</span>
      <span>vanilla 1.3%</span>
      <span>fine-tuned 7.1%</span>
      <span class="rg-hot">+ compile-gated RAG 10.3%</span>
    </div>
  </div>
</div>"""


def backend_status() -> str:
    if CONFIG.backend == "mock":
        return "⚠ **mock backend** — model not yet loaded (set `RUSTGEN_BACKEND=hf`)"
    adapter = CONFIG.adapter_path or "no adapter"
    return f"**Backend:** `{CONFIG.base_model}` + `{adapter}`"


def verify_compiles(code: str, tests: str | None = None) -> str:
    """Compile (and optionally test-run) the generated function with rustc."""
    if shutil.which("rustc") is None:
        return "rustc not installed — compile check skipped (install via https://rustup.rs)"
    try:
        result = run_rust(code, tests or "fn main() {}")
    except Exception as exc:  # never let verification take the demo down
        return f"verification error: {exc}"
    if result.passed:
        if tests:
            n = tests.count("assert")
            return f"✓ compiles AND passes {n} model-generated tests (indicative, not ground truth)"
        return "✓ compiles (rustc)"
    first_lines = "\n".join(result.stderr.strip().splitlines()[:12])
    if tests and result.stage == "run":
        return f"✗ compiled, but FAILED the model-generated tests:\n{first_lines}"
    return f"✗ {result.stage} failed:\n{first_lines}"


def draft_python(description: str) -> tuple[str | None, str]:
    """Run the pivot drafter; never raise. Returns (python_or_none, panel_note)."""
    if CONFIG.backend == "mock":
        return None, "// pivot skipped: mock backend (set RUSTGEN_BACKEND=hf)"
    try:
        drafted = DRAFTER.draft(description)
    except Exception as exc:
        return None, f"// pivot drafter failed ({exc}) — fell back to direct English→Rust"
    if drafted is None:
        return None, "// drafter produced no usable function — fell back to direct English→Rust"
    return drafted, drafted


def draft_signature(description: str, python: str | None) -> str | None:
    """Ask the drafter for a Rust signature; never raise."""
    if CONFIG.backend == "mock":
        return None
    try:
        return DRAFTER.draft_signature(description, python)
    except Exception:
        return None


def draft_rust_tests(description: str, signature: str) -> tuple[str | None, str]:
    """Ask the drafter for assert_eq! tests; never raise."""
    if CONFIG.backend == "mock":
        return None, "// test generation skipped: mock backend"
    if not signature.strip():
        return None, "// test generation needs a Rust signature — none given"
    try:
        tests = DRAFTER.draft_tests(description, signature)
    except Exception as exc:
        return None, f"// test drafter failed ({exc}) — compile check only"
    if tests is None:
        return None, "// drafter produced no usable fn main — compile check only"
    return tests, tests


def _pipeline_line(route: str, verify: str, cascade_trail: str) -> str:
    if verify.startswith("✓"):
        icon = "✅"
    elif "skipped" in verify or "not installed" in verify:
        icon = "⚠️"
    else:
        icon = "❌"
    line = f"**Pipeline:**  {route} → fine-tuned codegen-350M → Rust → rustc {icon}"
    if cascade_trail:
        line += f"  \n**Compile-gated cascade:** {cascade_trail}"
    return line


def _quick_compiles(code: str) -> bool | None:
    """Fast compile-only probe for the cascade. None = can't check (no rustc)."""
    if shutil.which("rustc") is None:
        return None
    try:
        return run_rust(code, "fn main() {}").passed
    except Exception:
        return None


def translate(description: str, python_code: str, signature: str,
              use_pivot: bool, draft_sig: bool, gen_tests: bool,
              use_cascade: bool, drafted_state: dict | None = None):
    prev_drafts = drafted_state or {}
    python = (python_code or "").strip() or None
    description = description.strip()
    if not description and python is None:
        return ("", "// Give an English description, Python code, or both.",
                "", "", "", gr.update(), gr.update(), prev_drafts)
    if not description:
        description = GENERIC_DESCRIPTION

    # Route: pasted Python beats drafting; empty Python box + pivot = Qwen
    # drafts it. Drafted artifacts are written BACK INTO the form boxes, so
    # the audience sees them and the presenter can edit + re-run.
    python_was_drafted = False
    if python is not None:
        route = "your Python"
    elif use_pivot:
        python, note = draft_python(description)
        if python:
            python_was_drafted = True
            route = "English → *Qwen drafts Python*"
        elif "skipped" in note:
            route = "English (direct — pivot skipped)"
        else:
            route = "English (direct — draft failed)"
    else:
        route = "English (direct)"

    # Empty signature box: let Qwen anchor the translation (and enable tests).
    signature = signature.strip()
    sig_was_drafted = False
    if not signature and draft_sig:
        drafted = draft_signature(description, python)
        if drafted:
            signature = drafted
            sig_was_drafted = True
            route += " → *Qwen drafts signature*"

    task = TranslationTask(
        description=description,
        python_code=python,
        signature=signature or None,
    )

    # Retrieval query: the Python source when we have it — code-to-code
    # similarity is the signal the RAG index is built for.
    query = python or description

    def examples_for(k: int) -> list[str]:
        return RETRIEVER.retrieve(query, k) if k > 0 else []

    # Attempt plan — the measured Step 4 policy (7.1% → 10.3%): lead WITHOUT
    # retrieval (the fine-tune's strongest configuration), and only on compile
    # failure retry with retrieved examples, k=1 then k=4. Compile success is
    # the only gating signal — never the tests.
    plan = [0] + ([1, 4] if use_cascade else [])

    trail, rust, chosen_examples = [], "", []
    attempt_log = []  # (label, compiled_ok, examples) for the retrieved panel
    for attempt_k in plan:
        task.context_examples = examples_for(attempt_k)
        candidate = TRANSLATOR.generate(task)
        ok = _quick_compiles(candidate)
        label = f"RAG k={attempt_k}" if attempt_k else "RAG off"
        attempt_log.append((label, ok, task.context_examples))
        if ok is None:  # rustc unavailable: no gate to cascade on
            rust, chosen_examples = candidate, task.context_examples
            break
        trail.append(("✅" if ok else "❌") + " " + label)
        if ok or not rust:  # keep the first output, upgrade on first success
            rust, chosen_examples = candidate, task.context_examples
        if ok:
            break

    # Show what EVERY attempt retrieved, labeled by outcome — not just the
    # attempt whose output is displayed (an all-fail cascade still retrieved).
    parts = []
    for label, ok, exs in attempt_log:
        if not exs:
            continue
        fate = "→ this is the output shown" if exs is chosen_examples else "output discarded"
        compiled = "compiled" if ok else ("compile check unavailable" if ok is None else "failed to compile")
        parts.append(f"// ===== attempt {label} ({compiled}; {fate}) =====\n\n"
                     + "\n\n".join(exs))
    retrieved = "\n\n".join(parts)

    tests, tests_panel = (None, "")
    if gen_tests:
        tests, tests_panel = draft_rust_tests(description, signature)
    verify = verify_compiles(rust, tests)
    cascade_trail = " → ".join(trail) if len(trail) > 1 else ""
    pipeline = _pipeline_line(route, verify, cascade_trail)

    # Fill drafted artifacts into the form; gr.update() = leave box untouched.
    py_update = gr.update(value=python) if python_was_drafted else gr.update()
    sig_update = gr.update(value=signature) if sig_was_drafted else gr.update()

    # Remember what is model-drafted (surviving re-runs with the same draft),
    # so editing the description can auto-clear stale drafts — but never wipe
    # content the user typed or pasted themselves.
    new_drafts = {
        "python": python if python_was_drafted or (
            python and python == prev_drafts.get("python")) else "",
        "signature": signature if sig_was_drafted or (
            signature and signature == prev_drafts.get("signature")) else "",
    }
    return (pipeline, rust, verify, tests_panel, retrieved,
            py_update, sig_update, new_drafts)


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="RustGen", css=_CSS) as demo:
        gr.HTML(_header_html())
        gr.Markdown(backend_status())
        with gr.Row(equal_height=False):
            with gr.Column(scale=5):
                description = gr.Textbox(
                    label="What should the function do? (English)", lines=2,
                    placeholder="e.g. Count how many numbers in a vector are even.")
                python_code = gr.Code(
                    language="python",
                    label="Python implementation — optional: leave empty and Qwen drafts it")
                signature = gr.Textbox(
                    label="Rust signature — optional: leave empty and Qwen drafts it",
                    placeholder="fn count_even(nums: Vec<isize>) -> isize")
                with gr.Accordion("Generated tests (model-written)", open=False):
                    tests_out = gr.Code(language=RUST_LANG, label="assert_eq! checks")
                go = gr.Button("Translate to Rust", variant="primary", size="lg")
                with gr.Accordion("Options", open=False):
                    use_pivot = gr.Checkbox(
                        label=f"Draft Python with {CONFIG.pivot_model.split('/')[-1]} "
                              "when the Python box is empty (pivot route)",
                        value=True)
                    draft_sig = gr.Checkbox(
                        label="Draft the Rust signature when the box is empty (Qwen)",
                        value=True)
                    gen_tests = gr.Checkbox(
                        label="Generate tests and run them (model-written)",
                        value=True)
                    use_cascade = gr.Checkbox(
                        label="RAG via compile-gated cascade: when compilation fails, "
                              "retry with retrieved examples (k=1, then k=4) — "
                              "our measured 7.1% → 10.3% policy",
                        value=True)
            with gr.Column(scale=6):
                pipeline_out = gr.Markdown("")
                rust_out = gr.Code(language=RUST_LANG, label="Rust")
                verify_out = gr.Textbox(label="Verification (rustc)", lines=2)
                with gr.Accordion("Retrieved examples (RAG)", open=False):
                    retrieved_out = gr.Code(language=RUST_LANG, label="RAG context")

        drafted_state = gr.State({})   # what the model drafted last run

        inputs = [description, python_code, signature, use_pivot, draft_sig,
                  gen_tests, use_cascade]
        panels = [pipeline_out, rust_out, verify_out, tests_out, retrieved_out]

        # Stale-output guard: USER edits (typing, toggles) invalidate the
        # previous answer. `.input` fires only on user interaction — critical,
        # because translate() programmatically fills the Python/signature
        # boxes and must not trigger a wipe of its own results.
        def clear_panels():
            return "", "", "", "", ""

        for component in inputs:
            listener = getattr(component, "input", component.change)
            listener(clear_panels, None, panels)

        # Stale-DRAFT guard: typing a new description clears any box that
        # still holds an UNEDITED model draft from the previous run —
        # otherwise old drafts masquerade as "your Python" for the new ask.
        # Content the user typed/pasted themselves is never touched.
        def clear_stale_drafts(python_val, sig_val, drafts):
            drafts = drafts or {}
            py_update = sig_update = gr.update()
            if drafts.get("python") and (python_val or "").strip() == drafts["python"].strip():
                py_update = gr.update(value="")
            if drafts.get("signature") and (sig_val or "").strip() == drafts["signature"].strip():
                sig_update = gr.update(value="")
            return py_update, sig_update

        desc_listener = getattr(description, "input", description.change)
        desc_listener(clear_stale_drafts, [python_code, signature, drafted_state],
                      [python_code, signature])

        # Clear first, then generate — the visible blank is the "working" cue.
        # translate also writes drafted Python/signature into the form boxes.
        go.click(clear_panels, None, panels).then(
            translate, inputs + [drafted_state],
            panels + [python_code, signature, drafted_state])

        # Every row below was battery-tested against the fine-tuned model on
        # 2026-07-11: all compile with correct logic on the FIRST (RAG-free)
        # attempt, so the cascade stays quiet. is_not_prime keeps test-gen OFF
        # (Qwen's test rightly flags the n=1 edge case that the MBPP reference
        # itself gets wrong). The last row is the full pivot: empty Python box,
        # Qwen drafts Python + signature, tests pass 3/3.
        examples = gr.Examples(
            examples=[
                ["Identify non-prime numbers.",
                 "import math\ndef is_not_prime(n):\n    result = False\n"
                 "    for i in range(2, int(math.sqrt(n)) + 1):\n"
                 "        if n % i == 0:\n            result = True\n    return result",
                 "fn is_not_prime(n: isize) -> bool", True, True, False, True],
                ["Count how many numbers in a vector are even.",
                 "def count_even(nums):\n    return sum(1 for n in nums if n % 2 == 0)",
                 "fn count_even(nums: Vec<isize>) -> isize", True, True, True, True],
                ["Find the smallest number in a vector.",
                 "def minimum(nums):\n    smallest = nums[0]\n    for x in nums:\n"
                 "        if x < smallest:\n            smallest = x\n    return smallest",
                 "fn minimum(nums: Vec<isize>) -> isize", True, True, True, True],
                ["Compute the factorial of n.",
                 "def factorial(n):\n    result = 1\n    for i in range(2, n + 1):\n"
                 "        result *= i\n    return result",
                 "fn factorial(n: u64) -> u64", True, True, True, True],
                ["Count how many numbers in a vector are even.", "",
                 "fn count_even(nums: Vec<isize>) -> isize", True, True, True, True],
            ],
            inputs=inputs,
            elem_id="rg-examples",
            label="Try these — click a row to fill the form (last row lets Qwen draft the Python)",
        )
        # Example rows fill the form programmatically, which `.input` ignores —
        # clear the result panels on row click too, where the API allows it.
        try:
            examples.dataset.click(clear_panels, None, panels)
        except AttributeError:
            pass
    return demo


if __name__ == "__main__":
    build_demo().launch()
