"""Ask Agent — read-only Q&A over a repo workspace."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Generator

from agent.llms import codegen_generate
from agent.repo_utils import (
    append_bot,
    append_user,
    detect_ask_task,
    empty_session,
    extract_file_refs,
    format_sources_block,
    load_context_sources,
    resolve_repo_root,
    set_active_files,
    strip_task_prefix,
    trim_sources_for_prompt,
    update_last_bot,
    yield_chat,
)
from data.scripts.prompt_templates import (
    format_file_ask_inference,
    format_folder_ask_inference,
    format_nl2java_inference,
    format_nl2py_inference,
)

STATE_INIT = "init"
STATE_QA = "qa"


def _default_question() -> str:
    return "Summarize what this folder contains and explain the main functionality."


def _is_generic_multi_file_question(question: str) -> bool:
    lower = question.strip().lower()
    if not lower:
        return True
    generic_patterns = (
        r"\bselected files?\b",
        r"\bthese files?\b",
        r"\bthe files?\b",
        r"\bexplain (the )?(selected )?files?\b",
        r"\bsummarize (the )?(selected )?files?\b",
        r"\bdescribe (the )?(selected )?files?\b",
    )
    if any(re.search(p, lower) for p in generic_patterns):
        return True
    return lower in {
        "explain",
        "summarize",
        "describe",
        "what is this",
        "what does this do",
    }


def _question_for_file(
    question: str, file_name: str, index: int, total: int
) -> str:
    """Use a file-specific question so the model does not repeat a file list."""
    if _is_generic_multi_file_question(question):
        base = Path(file_name).name
        return (
            f"Write plain documentation for `{base}` explaining what it does "
            f"and its role in the project. (File {index} of {total}.)"
        )
    return question.strip()


def _answer_question(
    history: list[dict[str, str]],
    session_state: dict[str, Any],
    root: str,
    question: str,
    sources: list[dict[str, str]],
) -> Generator[dict[str, Any], None, None]:
    focused = trim_sources_for_prompt(sources)
    if not focused:
        update_last_bot(history, "No source files were loaded.")
        yield yield_chat(history, {"session_state": session_state})
        return

    if len(focused) == 1:
        source = focused[0]
        prompt = format_folder_ask_inference(
            repo_root=root,
            file_list=source["name"],
            sources=format_sources_block([source], for_doc=True),
            question=question,
        )
        answer = codegen_generate(prompt, response_type="doc", max_new_tokens=768)
        update_last_bot(history, answer or "(No answer generated.)")
        yield yield_chat(history, {"session_state": session_state})
        return

    sections: list[str] = []
    total = len(focused)
    sections.extend([
        f"**Selected files ({total}):**",
        *[f"{i}. `{s['name']}`" for i, s in enumerate(focused, start=1)],
        "",
    ])
    for index, source in enumerate(focused, start=1):
        update_last_bot(
            history,
            f"Explaining file {index}/{total}: `{source['name']}`...",
        )
        yield yield_chat(history, {"session_state": session_state})

        file_question = _question_for_file(question, source["name"], index, total)
        prompt = format_file_ask_inference(
            repo_root=root,
            file_name=source["name"],
            source=format_sources_block([source], for_doc=True),
            question=file_question,
        )
        section = codegen_generate(prompt, response_type="doc", max_new_tokens=768)
        body = section or "(No answer generated.)"
        sections.append(f"### {Path(source['name']).name}\n{body}")

    update_last_bot(history, "\n".join(sections))
    yield yield_chat(history, {"session_state": session_state})


def _generate_code_in_chat(
    task: str,
    spec: str,
    history: list[dict[str, str]],
    session_state: dict[str, Any],
) -> Generator[dict[str, Any], None, None]:
    """Generate NL→code and return a fenced block in chat (no file writes)."""
    if task == "gen_python":
        prompt = format_nl2py_inference(spec)
        fence = "python"
    else:
        prompt = format_nl2java_inference(spec)
        fence = "java"

    code = codegen_generate(prompt, response_type="code")
    if code and code.strip():
        answer = f"```{fence}\n{code.strip()}\n```"
    else:
        answer = "(No code generated.)"
    update_last_bot(history, answer)
    yield yield_chat(history, {"session_state": session_state})


def chat_ask_generator(
    user_message: str,
    history: list[dict[str, str]],
    session_state: dict[str, Any],
    repo_root: str,
    max_files: int = 20,
) -> Generator[dict[str, Any], None, None]:
    if not session_state:
        session_state = empty_session(repo_root)

    if repo_root:
        session_state["repo_root"] = repo_root

    question = user_message.strip()
    task = detect_ask_task(user_message)
    body = strip_task_prefix(user_message)

    if task in ("gen_python", "gen_java"):
        append_user(history, user_message)
        append_bot(history, "Generating code...")
        yield yield_chat(history, {"session_state": session_state})
        yield from _generate_code_in_chat(
            task, body or user_message, history, session_state
        )
        return

    root = (session_state.get("repo_root") or "").strip()
    if not root:
        append_user(history, user_message)
        append_bot(history, "Set the **Project root** path above, then ask your question.")
        yield yield_chat(history, {"session_state": session_state})
        return

    active_files = session_state.get("active_files") or []
    has_file_target = bool(extract_file_refs(question)) or bool(active_files)
    current = session_state.get("state", STATE_INIT)
    cached_sources = session_state.get("sources_cache") or []

    if has_file_target:
        append_user(history, user_message)
        status = "Thinking..." if current == STATE_QA else "Analyzing selected files..."
        append_bot(history, status)
        yield yield_chat(history, {"session_state": session_state})

        try:
            resolve_repo_root(root)
        except FileNotFoundError:
            update_last_bot(history, f"Repo path not found: `{root}`")
            yield yield_chat(history, {"session_state": session_state})
            return

        sources, files, err = load_context_sources(
            root, question, active_files, max_files=max_files
        )
        if err:
            update_last_bot(history, err)
            yield yield_chat(history, {"session_state": session_state})
            return

        set_active_files(session_state, root, files)
        session_state["file_index"] = files
        session_state["sources_cache"] = sources
        session_state["state"] = STATE_QA

        if not question:
            question = _default_question()

        loaded_names = ", ".join(s["name"] for s in sources)
        if len(sources) < len(files):
            update_last_bot(
                history,
                f"Reading {len(sources)} of {len(files)} file(s) ({loaded_names})... generating answer.",
            )
        else:
            update_last_bot(
                history,
                f"Reading {len(sources)} file(s)... generating answer.",
            )
        yield yield_chat(history, {"session_state": session_state})
        yield from _answer_question(history, session_state, root, question, sources)
        return

    if current == STATE_QA and cached_sources:
        append_user(history, user_message)
        append_bot(history, "Thinking...")
        yield yield_chat(history, {"session_state": session_state})
        yield from _answer_question(
            history,
            session_state,
            session_state.get("repo_root", root),
            question or _default_question(),
            cached_sources,
        )
        return

    session_state["state"] = STATE_INIT
    append_user(history, user_message)
    append_bot(history, "Analyzing repository...")
    yield yield_chat(history, {"session_state": session_state})

    try:
        resolve_repo_root(root)
    except FileNotFoundError:
        update_last_bot(history, f"Repo path not found: `{root}`")
        yield yield_chat(history, {"session_state": session_state})
        return

    sources, files, err = load_context_sources(root, question, [], max_files=max_files)
    if err:
        update_last_bot(history, err)
        yield yield_chat(history, {"session_state": session_state})
        return

    set_active_files(session_state, root, files)
    session_state["file_index"] = files
    session_state["sources_cache"] = sources
    session_state["state"] = STATE_QA

    if not question:
        question = _default_question()

    update_last_bot(history, f"Reading {len(sources)} file(s)... generating answer.")
    yield yield_chat(history, {"session_state": session_state})

    yield from _answer_question(history, session_state, root, question, sources)


def strip_migrate_prefix(question: str) -> str:
    lower = question.lower()
    if lower.startswith("migrate"):
        return question[7:].strip(" :—-")
    return question
