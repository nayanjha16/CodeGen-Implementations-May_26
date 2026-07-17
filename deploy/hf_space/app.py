"""Gradio demo for the Qwen multi-task code model + agent selection UI."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import gradio as gr

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
# Ensure project root is on path so `agent` and local packages import when
# launched from deploy/hf_space via scripts/run_local_gradio.py
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from generator import CodeGenerator
from prompt_templates import (
    format_code2doc_inference,
    format_java2py_inference,
    format_nl2py_inference,
)

DEFAULT_LOCAL = PROJECT_ROOT / "models" / "qwen_multitask" / "merged"
HF_DEFAULT = "Saikrishna2511/qwen-multitask"

MODEL_ID = os.environ.get("MODEL_ID") or (
    str(DEFAULT_LOCAL.resolve()) if DEFAULT_LOCAL.exists() else HF_DEFAULT
)
_generator: CodeGenerator | None = None

MODE_GENERATE = "Generate Agent"
MODE_FIX = "Fix Agent"
MODE_FULL = "Full loop (Generate + Fix)"


def get_generator() -> CodeGenerator:
    global _generator
    if _generator is None:
        _generator = CodeGenerator(model_path=MODEL_ID)
    return _generator


def _wire_codegen() -> None:
    from agent.llms import set_codegen_generator

    set_codegen_generator(get_generator())


def run_nl2py(
    query: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
) -> str:
    if not query.strip():
        return "Please enter a natural language description."
    prompt = format_nl2py_inference(query)
    return get_generator().generate(
        prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        response_type="code",
    )


def run_java2py(
    java_code: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
) -> str:
    if not java_code.strip():
        return "Please enter Java source code."
    prompt = format_java2py_inference(java_code)
    return get_generator().generate(
        prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        response_type="code",
    )


def run_code2doc(
    python_code: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
) -> str:
    if not python_code.strip():
        return "Please enter Python source code."
    prompt = format_code2doc_inference(python_code)
    return get_generator().generate(
        prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        response_type="doc",
    )


def run_selected_agent(
    mode: str,
    prompt: str,
    python_code: str,
    runtime: str,
    unit: str,
    max_retries: int,
    use_rag: bool,
):
    """Dispatch to Generate / Fix / Full-loop based on UI radio."""
    empty = ("", "", "", "", "", 0, [])
    try:
        _wire_codegen()
        unit_val = "class" if unit == "class" else "function"

        if mode == MODE_GENERATE:
            if not prompt.strip():
                return ("", "", "Error", "Prompt is required for Generate Agent", "", 0, [])
            from agent.ui_runners import run_generate_agent

            out = run_generate_agent(prompt, unit=unit_val, use_rag=bool(use_rag))
            return (
                out.get("java_code") or "",
                out.get("python_code") or "",
                "n/a (Generate only)",
                "",
                out.get("unit") or unit_val,
                0,
                out.get("trace") or [],
            )

        if mode == MODE_FIX:
            if not (python_code or "").strip():
                return ("", "", "Error", "Python code is required for Fix Agent", "", 0, [])
            from agent.ui_runners import run_fix_agent

            out = run_fix_agent(
                prompt,
                python_code,
                runtime=runtime or "",
                unit=unit_val,
            )
            return (
                "",
                out.get("python_code") or "",
                "n/a (Fix only — see Python output)",
                out.get("ast_info") or "",
                out.get("unit") or unit_val,
                0,
                out.get("trace") or [],
            )

        # Full loop
        if not prompt.strip():
            return ("", "", "Error", "Prompt is required for Full loop", "", 0, [])
        from agent.graph import solve

        out = solve(
            prompt,
            unit=unit_val,
            use_rag=bool(use_rag),
            max_retries=int(max_retries),
        )
        yes = bool(out.get("judge_yes"))
        return (
            out.get("java_code") or "",
            out.get("python_code") or "",
            "YES" if yes else "NO",
            out.get("judge_reason") or "",
            out.get("unit") or unit_val,
            int(out.get("attempts") or 0),
            out.get("trace") or [],
        )
    except Exception as e:
        return ("", "", "Error", str(e), "", 0, [])


def on_mode_change(mode: str):
    """Show/hide Fix-only and Full-loop controls."""
    is_fix = mode == MODE_FIX
    is_full = mode == MODE_FULL
    is_gen = mode == MODE_GENERATE
    # python_code + runtime visible for Fix; max_retries for Full; use_rag for Gen/Full
    return (
        gr.update(visible=is_fix),  # python_code
        gr.update(visible=is_fix),  # runtime
        gr.update(visible=is_full),  # max_retries
        gr.update(visible=is_gen or is_full),  # use_rag
        gr.update(
            value=(
                "Run Generate Agent"
                if is_gen
                else "Run Fix Agent"
                if is_fix
                else "Run Full Agent Loop"
            )
        ),
    )


NL2PY_EXAMPLES = [
    ["Write a function that returns the factorial of n"],
    ["Given a list of integers, return the two numbers that add up to a target sum."],
]

JAVA2PY_EXAMPLES = [
    [
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        System.out.println(1);\n"
        "    }\n"
        "}"
    ],
    [
        "public int add(int a, int b) {\n"
        "    return a + b;\n"
        "}"
    ],
]

CODE2DOC_EXAMPLES = [
    ["def add(a, b):\n    return a + b"],
    [
        "def merge_sort(arr):\n"
        "    if len(arr) <= 1:\n"
        "        return arr\n"
        "    mid = len(arr) // 2\n"
        "    left = merge_sort(arr[:mid])\n"
        "    right = merge_sort(arr[mid:])\n"
        "    return merge(left, right)"
    ],
]

AGENT_EXAMPLES = [
    [MODE_GENERATE, "Write a program that prints the sum of 2 and 3.", "", "", "function"],
    [
        MODE_FIX,
        "Print the sum of 2 and 3.",
        "print(2 +",
        "SyntaxError: '(' was never closed",
        "function",
    ],
    [MODE_FULL, "Write a program that prints the sum of 2 and 3.", "", "", "function"],
]


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="Qwen Multitask Code Assistant") as demo:
        gr.Markdown(
            f"# Qwen Multitask Code Assistant\n"
            f"Fine-tuned model: `{MODEL_ID}`\n\n"
            "Use the task tabs for single-shot codegen, or the **Agent** tab to "
            "select **Generate Agent**, **Fix Agent**, or the full "
            "Generate → run → judge → Fix loop."
        )

        with gr.Row():
            max_tokens = gr.Slider(64, 1024, value=512, step=64, label="Max new tokens")
            temperature = gr.Slider(0.0, 1.0, value=0.2, step=0.05, label="Temperature")
            top_p = gr.Slider(0.5, 1.0, value=0.95, step=0.05, label="Top-p")

        with gr.Tabs():
            with gr.Tab("NL → Python"):
                nl_input = gr.Textbox(
                    label="Natural language description",
                    lines=4,
                    placeholder="Write a function that checks if a string is a palindrome.",
                )
                nl_output = gr.Code(
                    label="Generated Python",
                    language="python",
                    interactive=False,
                )
                nl_btn = gr.Button("Generate Python", variant="primary")
                nl_btn.click(
                    run_nl2py,
                    inputs=[nl_input, max_tokens, temperature, top_p],
                    outputs=nl_output,
                )
                gr.Examples(examples=NL2PY_EXAMPLES, inputs=nl_input)

            with gr.Tab("Java → Python"):
                java_input = gr.Textbox(
                    label="Java source code",
                    lines=12,
                    max_lines=24,
                    placeholder="public class Main {\n    public static void main(String[] args) { ... }\n}",
                )
                java_output = gr.Code(
                    label="Generated Python",
                    language="python",
                    interactive=False,
                )
                java_btn = gr.Button("Translate to Python", variant="primary")
                java_btn.click(
                    run_java2py,
                    inputs=[java_input, max_tokens, temperature, top_p],
                    outputs=java_output,
                )
                gr.Examples(examples=JAVA2PY_EXAMPLES, inputs=java_input)

            with gr.Tab("Code → Documentation"):
                py_input = gr.Textbox(
                    label="Python source code",
                    lines=12,
                    max_lines=24,
                    placeholder="def add(a, b):\n    return a + b",
                )
                doc_output = gr.Textbox(label="Generated documentation", lines=10)
                doc_btn = gr.Button("Generate documentation", variant="primary")
                doc_btn.click(
                    run_code2doc,
                    inputs=[py_input, max_tokens, temperature, top_p],
                    outputs=doc_output,
                )
                gr.Examples(examples=CODE2DOC_EXAMPLES, inputs=py_input)

            with gr.Tab("Agent"):
                gr.Markdown(
                    "Select an agent mode:\n"
                    "- **Generate Agent** — NL → Java → Python\n"
                    "- **Fix Agent** — repair Python using the error + original request\n"
                    "- **Full loop** — Generate → sandbox → judge → Fix until YES"
                )
                agent_mode = gr.Radio(
                    choices=[MODE_GENERATE, MODE_FIX, MODE_FULL],
                    value=MODE_GENERATE,
                    label="Agent mode",
                )
                agent_prompt = gr.Textbox(
                    label="Natural language request",
                    lines=3,
                    placeholder="Write a program that prints the sum of 2 and 3.",
                )
                agent_unit = gr.Radio(
                    choices=["function", "class"],
                    value="function",
                    label="Unit",
                )
                agent_python = gr.Code(
                    label="Python to fix (Fix Agent)",
                    language="python",
                    visible=False,
                )
                agent_runtime = gr.Textbox(
                    label="Runtime / error (Fix Agent)",
                    lines=4,
                    visible=False,
                    placeholder="SyntaxError: ...",
                )
                agent_retries = gr.Slider(
                    0,
                    5,
                    value=3,
                    step=1,
                    label="Max fix retries (Full loop)",
                    visible=False,
                )
                agent_rag = gr.Checkbox(
                    label="Use RAG retrieve",
                    value=False,
                    visible=True,
                )
                agent_btn = gr.Button("Run Generate Agent", variant="primary")

                with gr.Row():
                    agent_java = gr.Code(label="Java", interactive=False)
                    agent_py_out = gr.Code(
                        label="Python",
                        language="python",
                        interactive=False,
                    )
                agent_judge = gr.Textbox(label="Judge (Full loop only)", interactive=False)
                agent_reason = gr.Textbox(
                    label="Judge reason (Full) / AST before→after (Fix)",
                    lines=3,
                    interactive=False,
                )
                agent_unit_out = gr.Textbox(label="Unit", interactive=False)
                agent_attempts = gr.Number(label="Attempts", interactive=False)
                agent_trace = gr.JSON(label="Trace")

                agent_mode.change(
                    on_mode_change,
                    inputs=[agent_mode],
                    outputs=[
                        agent_python,
                        agent_runtime,
                        agent_retries,
                        agent_rag,
                        agent_btn,
                    ],
                )
                agent_btn.click(
                    run_selected_agent,
                    inputs=[
                        agent_mode,
                        agent_prompt,
                        agent_python,
                        agent_runtime,
                        agent_unit,
                        agent_retries,
                        agent_rag,
                    ],
                    outputs=[
                        agent_java,
                        agent_py_out,
                        agent_judge,
                        agent_reason,
                        agent_unit_out,
                        agent_attempts,
                        agent_trace,
                    ],
                )
                def _load_agent_example(mode, prompt, python, runtime, unit):
                    """Fill example fields and sync Fix/Full visibility controls."""
                    is_fix = mode == MODE_FIX
                    is_full = mode == MODE_FULL
                    is_gen = mode == MODE_GENERATE
                    return (
                        mode,
                        prompt,
                        gr.update(value=python, visible=is_fix),
                        gr.update(value=runtime, visible=is_fix),
                        unit,
                        gr.update(visible=is_full),
                        gr.update(visible=is_gen or is_full),
                        gr.update(
                            value=(
                                "Run Generate Agent"
                                if is_gen
                                else "Run Fix Agent"
                                if is_fix
                                else "Run Full Agent Loop"
                            )
                        ),
                    )

                gr.Examples(
                    examples=AGENT_EXAMPLES,
                    inputs=[
                        agent_mode,
                        agent_prompt,
                        agent_python,
                        agent_runtime,
                        agent_unit,
                    ],
                    outputs=[
                        agent_mode,
                        agent_prompt,
                        agent_python,
                        agent_runtime,
                        agent_unit,
                        agent_retries,
                        agent_rag,
                        agent_btn,
                    ],
                    fn=_load_agent_example,
                    run_on_click=True,
                )

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("GRADIO_SERVER_PORT", "7860")),
    )
