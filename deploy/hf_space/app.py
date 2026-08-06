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

# Shared FT resolver when running from the full repo; Space-only deploy falls back.
try:
    from inference.generator import HF_FT_MODEL, resolve_codegen_model_id

    MODEL_ID = resolve_codegen_model_id()
except ImportError:
    HF_FT_MODEL = "Saikrishna2511/qwen-multitask"
    _local = PROJECT_ROOT / "models" / "qwen_multitask" / "merged"
    MODEL_ID = os.environ.get("MODEL_ID") or (
        str(_local.resolve()) if _local.exists() else HF_FT_MODEL
    )

_generator: CodeGenerator | None = None

MODE_ASK = "Ask Agent"
MODE_CODE = "Code Agent"
MODE_DEBUG = "Debug Agent"


def get_generator() -> CodeGenerator:
    global _generator
    if _generator is None:
        _generator = CodeGenerator(model_path=MODEL_ID)
    return _generator


def _wire_codegen() -> None:
    from agent.llms import set_codegen_generator

    set_codegen_generator(get_generator())


def _normalize_chat_history(history) -> list[dict[str, str]]:
    """Convert Gradio Chatbot history to simple {role, content} messages."""
    if not history:
        return []
    normalized: list[dict[str, str]] = []
    for msg in history:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role")
        if role not in ("user", "assistant", "system"):
            continue
        content = msg.get("content", "")
        if isinstance(content, list):
            parts: list[str] = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    parts.append(str(part.get("text", "")))
                elif isinstance(part, str):
                    parts.append(part)
            content = "\n".join(parts)
        normalized.append({"role": role, "content": str(content)})
    return normalized


def _build_review_markdown(review_data: list[dict]) -> str:
    """Render pending file changes as Markdown code blocks."""
    if not review_data:
        return ""
    sections: list[str] = []
    for entry in review_data:
        name = entry.get("name", "Unknown")
        lang = entry.get("language", "")
        java_code = str(entry.get("java") or "")
        python_code = str(entry.get("python") or entry.get("content") or "")
        if lang == "java" or (java_code and not python_code):
            sections.append(f"### {name}\n\n**Java**\n```java\n{java_code or entry.get('content', '')}\n```")
        elif java_code and python_code:
            sections.append(
                f"### {name}\n\n"
                f"**Java**\n```java\n{java_code}\n```\n\n"
                f"**Python**\n```python\n{python_code}\n```"
            )
        else:
            sections.append(f"### {name}\n\n**Python**\n```python\n{python_code}\n```")
    return "\n\n---\n\n".join(sections)


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


def on_repo_mode_change(mode: str):
    """Show/hide repo workspace controls per agent mode."""
    is_ask = mode == MODE_ASK
    is_code = mode == MODE_CODE
    is_debug = mode == MODE_DEBUG
    show_review = is_code or is_debug
    placeholder = (
        "Explain files or ask python: / java: for inline code"
        if is_ask
        else 'python: add login API — or select .java files and say "convert selected"'
        if is_code
        else "scan — fix @file.py — fix all migrated (uses Max fix retries slider)"
    )
    return (
        gr.update(placeholder=placeholder),
        gr.update(visible=show_review),
        gr.update(visible=show_review),
        gr.update(visible=is_code or is_debug),
    )


def _file_index_extensions(mode: str) -> str:
    if mode == MODE_DEBUG:
        return ".py"
    if mode == MODE_CODE:
        return ".java"
    return ".java,.py"


def refresh_repo_file_index(repo_root: str, mode: str, current_value=None):
    """Populate the filterable file picker from the project root."""
    from agent.repo_utils import list_repo_relative_files

    root = (repo_root or "").strip()
    current = list(current_value or [])
    if not root:
        return gr.update(choices=[], value=[], info="Set a project root to index files.")
    try:
        exts = _file_index_extensions(mode)
        paths = list_repo_relative_files(root, extensions=exts)
        info = f"{len(paths)} file(s) indexed."
        if len(paths) >= 5000:
            info += " (list truncated at 5000 files)"
        kept = [p for p in current if p in paths]
        return gr.update(choices=paths, value=kept, info=info)
    except FileNotFoundError:
        return gr.update(choices=[], value=[], info="Project root path not found.")
    except Exception as exc:
        return gr.update(choices=[], value=[], info=f"Could not index files: {exc}")


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

def build_ui() -> gr.Blocks:
    with gr.Blocks(title="Qwen Multitask Code Assistant") as demo:
        gr.Markdown(
            f"# Qwen Multitask Code Assistant\n"
            f"Fine-tuned model: `{MODEL_ID}`\n\n"
            "Use the task tabs for single-shot codegen, or the **Agent** tab for "
            "repo workspace agents: **Ask**, **Code**, and **Debug**."
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
                    "### Repo workspace\n"
                    "Set a **project root** folder and chat:\n"
                    "- **Ask Agent** — summarize/explain repo contents (read-only)\n"
                    "- **Code Agent** — generate or edit Java/Python files in the repo\n"
                    "- **Debug Agent** — scan and fix Python validation errors\n\n"
                    "Select context files from the picker, or mention `@path/to/file.java` in chat — "
                    "selections sync automatically. "
                    "Code and Debug agents queue writes for **Review → Keep All / Undo All**."
                )
                repo_root_input = gr.Textbox(
                    label="Project root",
                    lines=1,
                    placeholder="/path/to/your/repo (e.g. /Users/you/javarepo/)",
                )
                with gr.Row():
                    repo_file_picker = gr.Dropdown(
                        label="Context files",
                        choices=[],
                        value=[],
                        multiselect=True,
                        filterable=True,
                        allow_custom_value=True,
                        interactive=True,
                        scale=4,
                        info="Type to filter, select one or more files, or mention @file in chat.",
                    )
                    btn_refresh_files = gr.Button("Refresh", scale=0, min_width=80)
                    btn_clear_context = gr.Button("Clear", scale=0, min_width=80)
                agent_mode = gr.Radio(
                    choices=[MODE_ASK, MODE_CODE, MODE_DEBUG],
                    value=MODE_ASK,
                    label="Agent mode",
                )
                agent_max_files = gr.Slider(
                    1,
                    20,
                    value=5,
                    step=1,
                    label="Max files to scan",
                )
                agent_retries = gr.Slider(
                    0,
                    5,
                    value=3,
                    step=1,
                    label="Max fix retries (Code Agent)",
                )

                repo_chatbot = gr.Chatbot(height=400, label="Repo Agent")
                with gr.Row():
                    repo_chat_input = gr.Textbox(
                        show_label=False,
                        placeholder="Ask about the repo, or @src/Main.java to focus",
                        scale=4,
                    )
                    repo_chat_submit = gr.Button("Send", variant="primary", scale=1)

                with gr.Row(visible=False) as review_buttons:
                    btn_review = gr.Button("Review", variant="primary")
                    btn_keep = gr.Button("Keep All", variant="secondary")
                    btn_undo = gr.Button("Undo All", variant="stop")

                review_panel = gr.Markdown(visible=False, label="Review")

                repo_session_state = gr.State({})

                def _handle_repo_chat(
                    mode, repo_root, selected_files, msg, history, state, max_ret, max_files
                ):
                    history = _normalize_chat_history(history)
                    if state is None:
                        state = {}
                    state["active_files"] = list(selected_files or [])
                    try:
                        _wire_codegen()
                        if mode == MODE_ASK:
                            from agent.repo_ask_chat import chat_ask_generator
                            gen = chat_ask_generator(
                                msg, history, state, repo_root or "", int(max_files)
                            )
                        elif mode == MODE_CODE:
                            from agent.repo_code_chat import chat_code_generator
                            gen = chat_code_generator(
                                msg,
                                history,
                                state,
                                repo_root or "",
                                int(max_ret),
                                int(max_files),
                            )
                        else:
                            from agent.repo_debug_chat import chat_debug_generator
                            gen = chat_debug_generator(
                                msg, history, state, repo_root or "", int(max_files), int(max_ret)
                            )

                        for update in gen:
                            hist = update.get("history", history)
                            new_state = update.get("session_state", state)
                            show_btns = update.get("show_action_buttons", False)
                            active = list((new_state or {}).get("active_files") or [])
                            yield (
                                "",
                                hist,
                                new_state,
                                gr.update(visible=show_btns),
                                gr.update(value="", visible=False),
                                gr.update(value=active),
                            )
                    except Exception as e:
                        err_history = list(history)
                        if not err_history or err_history[-1].get("content") != msg:
                            err_history.append({"role": "user", "content": msg})
                        err_history.append({"role": "assistant", "content": f"Error: {e}"})
                        active = list((state or {}).get("active_files") or [])
                        yield (
                            "",
                            err_history,
                            state,
                            gr.update(visible=False),
                            gr.update(visible=False),
                            gr.update(value=active),
                        )

                def _sync_picker_to_session(selected, state):
                    state = state or {}
                    state["active_files"] = list(selected or [])
                    return state

                def _clear_context(state):
                    state = state or {}
                    state["active_files"] = []
                    return state, gr.update(value=[])

                def _render_review(review_data):
                    if not review_data:
                        return gr.update(value="", visible=False)
                    return gr.update(value=_build_review_markdown(review_data), visible=True)

                def _handle_undo(state, history):
                    from agent.repo_utils import chat_action_undo
                    history = _normalize_chat_history(history)
                    update = chat_action_undo(state, history)
                    return (
                        update.get("history", history),
                        update.get("session_state", state),
                        gr.update(visible=False),
                        gr.update(visible=False),
                    )

                def _handle_keep(state, history):
                    from agent.repo_utils import chat_action_keep
                    history = _normalize_chat_history(history)
                    update = chat_action_keep(state, history)
                    return (
                        update.get("history", history),
                        update.get("session_state", state),
                        gr.update(visible=False),
                        gr.update(visible=False),
                    )

                def _handle_review(state, history):
                    from agent.repo_utils import chat_action_review, pending_to_review_data
                    history = _normalize_chat_history(history)
                    if state is None:
                        state = {}
                    update = chat_action_review(state, history)
                    data = update.get("review_data") or pending_to_review_data(state)
                    return (
                        update.get("history", history),
                        update.get("session_state", state),
                        gr.update(visible=True),
                        _render_review(data),
                    )

                chat_inputs = [
                    agent_mode,
                    repo_root_input,
                    repo_file_picker,
                    repo_chat_input,
                    repo_chatbot,
                    repo_session_state,
                    agent_retries,
                    agent_max_files,
                ]
                chat_outputs = [
                    repo_chat_input,
                    repo_chatbot,
                    repo_session_state,
                    review_buttons,
                    review_panel,
                    repo_file_picker,
                ]

                repo_chat_submit.click(_handle_repo_chat, inputs=chat_inputs, outputs=chat_outputs)
                repo_chat_input.submit(_handle_repo_chat, inputs=chat_inputs, outputs=chat_outputs)

                repo_file_picker.change(
                    _sync_picker_to_session,
                    inputs=[repo_file_picker, repo_session_state],
                    outputs=[repo_session_state],
                )

                btn_clear_context.click(
                    _clear_context,
                    inputs=[repo_session_state],
                    outputs=[repo_session_state, repo_file_picker],
                )

                btn_refresh_files.click(
                    refresh_repo_file_index,
                    inputs=[repo_root_input, agent_mode, repo_file_picker],
                    outputs=[repo_file_picker],
                )

                repo_root_input.change(
                    refresh_repo_file_index,
                    inputs=[repo_root_input, agent_mode, repo_file_picker],
                    outputs=[repo_file_picker],
                )

                btn_undo.click(
                    _handle_undo,
                    inputs=[repo_session_state, repo_chatbot],
                    outputs=[repo_chatbot, repo_session_state, review_buttons, review_panel],
                )
                btn_keep.click(
                    _handle_keep,
                    inputs=[repo_session_state, repo_chatbot],
                    outputs=[repo_chatbot, repo_session_state, review_buttons, review_panel],
                )
                btn_review.click(
                    _handle_review,
                    inputs=[repo_session_state, repo_chatbot],
                    outputs=[repo_chatbot, repo_session_state, review_buttons, review_panel],
                )

                agent_mode.change(
                    on_repo_mode_change,
                    inputs=[agent_mode],
                    outputs=[
                        repo_chat_input,
                        review_buttons,
                        review_panel,
                        agent_retries,
                    ],
                ).then(
                    refresh_repo_file_index,
                    inputs=[repo_root_input, agent_mode, repo_file_picker],
                    outputs=[repo_file_picker],
                )

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("GRADIO_SERVER_PORT", "7860")),
    )
