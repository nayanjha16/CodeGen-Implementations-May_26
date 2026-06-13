"""Gradio demo. Launch with: python -m rustgen.app.demo

Reads Config once at startup; the active backend is shown in the UI so the
demo-day mock -> real swap is provable.
"""

from __future__ import annotations

import gradio as gr

from rustgen.config import Config
from rustgen.rag import get_retriever
from rustgen.translator import get_translator
from rustgen.translator.base import TranslationTask

CONFIG = Config.from_env()
TRANSLATOR = get_translator(CONFIG)
RETRIEVER = get_retriever(CONFIG)

MODE_EN = "English → Rust"
MODE_PY = "Python → Rust"

# gradio's gr.Code has no Rust grammar (as of 6.x); fall back to plain text
RUST_LANG = "rust" if "rust" in gr.Code.languages else None


def backend_status() -> str:
    if CONFIG.backend == "mock":
        return "⚠ mock backend — model not yet trained"
    adapter = CONFIG.adapter_path or "no adapter"
    return f"{CONFIG.base_model} + {adapter}"


def translate(mode: str, description: str, python_code: str, signature: str,
              use_rag: bool, rag_k: float) -> tuple[str, str]:
    if not description.strip():
        return "// Enter an English description first.", ""
    task = TranslationTask(
        description=description.strip(),
        python_code=python_code.strip() if mode == MODE_PY and python_code.strip() else None,
        signature=signature.strip() or None,
    )
    if use_rag:
        task.context_examples = RETRIEVER.retrieve(task.description, int(rag_k))
    rust = TRANSLATOR.generate(task)
    retrieved = "\n\n".join(
        f"// --- retrieved example {i + 1} ---\n{ex}"
        for i, ex in enumerate(task.context_examples)
    )
    return rust, retrieved


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="RustGen") as demo:
        gr.Markdown("# RustGen — English / Python → Rust")
        gr.Markdown(f"**Backend:** {backend_status()}")
        with gr.Row():
            with gr.Column():
                mode = gr.Radio([MODE_EN, MODE_PY], value=MODE_EN, label="Mode")
                description = gr.Textbox(label="English description", lines=4,
                                         placeholder="e.g. Add two integers and return the sum.")
                python_code = gr.Code(language="python", label="Python code", visible=False)
                signature = gr.Textbox(label="Rust signature (optional)",
                                       placeholder="fn add(a: i64, b: i64) -> i64")
                use_rag = gr.Checkbox(label="Use RAG", value=CONFIG.rag_enabled)
                rag_k = gr.Slider(1, 5, value=CONFIG.rag_k, step=1, label="RAG examples (k)")
                go = gr.Button("Translate", variant="primary")
            with gr.Column():
                rust_out = gr.Code(language=RUST_LANG, label="Rust")
                with gr.Accordion("Retrieved examples", open=False):
                    retrieved_out = gr.Code(language=RUST_LANG, label="RAG context")

        mode.change(lambda m: gr.update(visible=(m == MODE_PY)), mode, python_code)
        inputs = [mode, description, python_code, signature, use_rag, rag_k]
        go.click(translate, inputs, [rust_out, retrieved_out])

        gr.Examples(
            examples=[
                [MODE_EN, "Add two integers and return the sum.", "",
                 "fn add(a: i64, b: i64) -> i64", False, 3],
                [MODE_EN, "Return the n-th Fibonacci number.", "", "", True, 3],
                [MODE_PY, "Reverse a string.",
                 "def reverse(s):\n    return s[::-1]",
                 "fn reverse(s: &str) -> String", False, 3],
            ],
            inputs=inputs,
        )
    return demo


if __name__ == "__main__":
    build_demo().launch()
