"""LangGraph node functions for the Ask Agent."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from agent.ask_query_planner import (
    ANSWER_MODE_CLARIFY,
    ANSWER_MODE_INVENTORY,
    ANSWER_MODE_PER_FILE,
    AskPlan,
    apply_plan_heuristics,
    build_retrieval_query,
    is_explicit_inventory_request,
    is_overview_question,
)
from agent.ask_state import AskAgentState, STATE_QA
from agent.repo_utils import (
    detect_ask_task,
    empty_session,
    extract_doc_file_refs,
    extract_file_refs,
    format_chat_history_block,
    format_sources_block,
    list_repo_relative_files,
    load_context_sources,
    resolve_repo_root,
    set_active_files,
    strip_task_prefix,
    trim_sources_for_prompt,
)
from data.scripts.prompt_templates import (
    format_file_ask_inference,
    format_folder_ask_inference,
    format_general_ask_inference,
    format_nl2java_inference,
    format_nl2py_inference,
    format_repo_inventory_ask_inference,
)
from utils.text_sanitize import truncate_roleplay_continuation

STATE_INIT = "init"

ASK_ANSWER_MAX_TOKENS = 256
RAG_SCORE_MARGIN = float(os.environ.get("RAG_SCORE_MARGIN", "0.08"))
RAG_OVERVIEW_SCORE_MARGIN = float(os.environ.get("RAG_OVERVIEW_SCORE_MARGIN", "0.15"))
ASK_FILE_EXTENSIONS = ".java,.py,.md"

_PROMPT_ECHO_PATTERNS = (
    r"^### Write plain-English",
    r"^### Answer the developer",
    r"^### Documentation:",
    r"^### Answer:",
    r"^Description:",
    r"^Use the code for context only",
)

_TRIVIAL_ANSWER_RE = re.compile(r"^(yes|no|ok|sure)\.?$", re.IGNORECASE)
_SHORT_ANSWER_LEN = 10
_UNRELIABLE_ANSWER = (
    "I couldn't generate a reliable answer from the retrieved context. "
    "Try asking about a specific file or rebuilding the RAG index."
)

_REPO_SCOPED_PATTERN_RE = (
    re.compile(r"\bthis repo\b"),
    re.compile(r"\bthis codebase\b"),
    re.compile(r"\bthis project\b"),
    re.compile(r"\bin the repo\b"),
    re.compile(r"\bin this repo\b"),
    re.compile(r"@\w"),
    re.compile(r"\.(?:java|py|md|txt|json|xml|yaml|yml)\b"),
)

_GENERIC_REPO_QUESTION_RE = (
    re.compile(r"^what is this\b"),
    re.compile(r"^what does this\b"),
    re.compile(r"\bwhere is\b"),
    re.compile(r"\bwho wrote\b"),
    re.compile(r"\boverview of this\b"),
    re.compile(r"\barchitecture of this\b"),
    re.compile(r"\bpurpose of this\b"),
)


def _ask_generate(prompt: str, *, max_new_tokens: int = ASK_ANSWER_MAX_TOKENS) -> str:
    from agent.repo_ask_chat import ask_generate

    return ask_generate(prompt, max_new_tokens=max_new_tokens)


def _codegen_generate(prompt: str, **kwargs: Any) -> str:
    from agent.repo_ask_chat import codegen_generate

    return codegen_generate(prompt, **kwargs)


def _plan_ask_query(question: str, history: list[dict[str, str]]):
    from agent.repo_ask_chat import plan_ask_query

    return plan_ask_query(question, history)


def _rag_index_exists(root: str) -> bool:
    from agent.repo_ask_chat import rag_index_exists

    return rag_index_exists(root)


def _get_repo_rag_pipeline(root: str):
    from agent.repo_ask_chat import get_repo_rag_pipeline

    return get_repo_rag_pipeline(root)


def _retrieve_sources_impl(*args: Any, **kwargs: Any):
    from agent.repo_ask_chat import _retrieve_sources

    return _retrieve_sources(*args, **kwargs)


def is_repo_scoped_question(message: str) -> bool:
    text = (message or "").strip()
    if not text:
        return False
    lower = text.lower()
    if any(p.search(lower) for p in _REPO_SCOPED_PATTERN_RE):
        return True
    if any(p.search(lower) for p in _GENERIC_REPO_QUESTION_RE):
        return True
    if extract_file_refs(text) or extract_doc_file_refs(text):
        return True
    return is_explicit_inventory_request(text)


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


def _overview_question_hint() -> str:
    return (
        " Use only the provided source snippets. Do not invent GitHub metadata, "
        "issue counts, commit history, or files not shown in the context."
    )


def _plan_from_dict(data: dict[str, Any] | None, question: str) -> AskPlan:
    if not data:
        return AskPlan(intent_summary=question, retrieval_query=question)
    return AskPlan(
        intent_summary=str(data.get("intent_summary", question)),
        retrieval_query=str(data.get("retrieval_query", question)),
        answer_mode=str(data.get("answer_mode", "direct_qa")),
        needs_repo_inventory=bool(data.get("needs_repo_inventory", False)),
        is_follow_up=bool(data.get("is_follow_up", False)),
    )


def _use_unified_answer(plan: AskPlan, sources: list[dict[str, str]]) -> bool:
    if len(sources) <= 1:
        return True
    if plan.answer_mode == ANSWER_MODE_PER_FILE:
        return False
    return True


def _context_header(total: int, from_rag: bool, scores: list[float] | None = None) -> str:
    if from_rag:
        if scores:
            lo, hi = min(scores), max(scores)
            return f"**Retrieved context ({total} chunks, scores {lo:.2f}–{hi:.2f}):**"
        return f"**Retrieved context ({total} chunks):**"
    return f"**Selected files ({total}):**"


def _format_source_listing(sources: list[dict[str, str]], from_rag: bool) -> list[str]:
    lines: list[str] = []
    for i, source in enumerate(sources, start=1):
        name = source.get("name", "")
        if from_rag:
            chunk_type = str(source.get("chunk_type") or "").strip()
            chunk_name = str(source.get("chunk_name") or "").strip()
            start_line = source.get("start_line")
            end_line = source.get("end_line")
            score = source.get("rag_score")
            detail = f"`{name}`"
            if chunk_type and chunk_name:
                detail += f" — {chunk_type} `{chunk_name}`"
            elif chunk_type:
                detail += f" — {chunk_type}"
            if start_line and end_line:
                detail += f" (L{start_line}–{end_line})"
            if score is not None:
                detail += f" · score {float(score):.2f}"
            lines.append(f"{i}. {detail}")
        else:
            lines.append(f"{i}. `{name}`")
    return lines


def _prepend_context_block(
    answer: str,
    sources: list[dict[str, str]],
    *,
    from_rag: bool,
) -> str:
    scores = [
        float(s.get("rag_score", 0))
        for s in sources
        if s.get("rag_score") is not None
    ]
    header = _context_header(len(sources), from_rag, scores or None)
    listing = "\n".join(_format_source_listing(sources, from_rag))
    return f"{header}\n{listing}\n\n{answer}"


def _question_for_file(
    question: str, file_name: str, index: int, total: int, intent_summary: str = ""
) -> str:
    if _is_generic_multi_file_question(question):
        base = Path(file_name).name
        return (
            f"Explain what `{base}` does and its role in the project. "
            f"(File {index} of {total}.)"
        )
    return intent_summary or question.strip()


def _repo_inventory_block(root: str) -> tuple[str, int]:
    files = list_repo_relative_files(root)
    if not files:
        return "(no source files found)", 0
    listing = "\n".join(f"- `{path}`" for path in files)
    return listing, len(files)


def _is_unreliable_answer(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if _TRIVIAL_ANSWER_RE.match(stripped):
        return True
    return len(stripped) < _SHORT_ANSWER_LEN


def sanitize_ask_response(text: str) -> str:
    raw = truncate_roleplay_continuation(text or "")
    if not raw:
        return _UNRELIABLE_ANSWER
    lines = raw.splitlines()
    cleaned: list[str] = []
    for line in lines:
        if any(re.match(p, line.strip(), flags=re.IGNORECASE) for p in _PROMPT_ECHO_PATTERNS):
            continue
        cleaned.append(line)
    body = "\n".join(cleaned).strip() or raw
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    deduped: list[str] = []
    for para in paragraphs:
        if deduped and para == deduped[-1]:
            continue
        deduped.append(para)
    result = "\n\n".join(deduped).strip()
    if not result or _is_unreliable_answer(result):
        return _UNRELIABLE_ANSWER
    return result


_sanitize_ask_response = sanitize_ask_response


def _ensure_session(state: AskAgentState) -> dict[str, Any]:
    session = state.get("session_state") or {}
    if not session:
        session = empty_session(state.get("repo_root", ""))
    if state.get("repo_root"):
        session["repo_root"] = state["repo_root"]
    return session


def detect_task(state: AskAgentState) -> dict[str, Any]:
    user_message = state.get("user_message", "")
    task_raw = detect_ask_task(user_message)
    task = "explain"
    if task_raw in ("gen_python", "gen_java"):
        task = task_raw
    return {
        "task": task,
        "question": user_message.strip(),
        "body": strip_task_prefix(user_message),
    }


def generate_code(state: AskAgentState) -> dict[str, Any]:
    task = state.get("task", "gen_python")
    spec = state.get("body") or state.get("user_message", "")
    if task == "gen_python":
        prompt = format_nl2py_inference(spec)
        fence = "python"
    else:
        prompt = format_nl2java_inference(spec)
        fence = "java"
    code = _codegen_generate(prompt, response_type="code")
    if code and code.strip():
        answer = f"```{fence}\n{code.strip()}\n```"
    else:
        answer = "(No code generated.)"
    return {"answer": answer, "done": True, "status": answer}


def check_no_repo(state: AskAgentState) -> dict[str, Any]:
    question = state.get("question", "")
    root = (_ensure_session(state).get("repo_root") or "").strip()
    if root:
        return {"route": "validate_repo"}
    if is_repo_scoped_question(question):
        return {
            "route": "repo_error",
            "answer": "Set the **Project root** path above, then ask your question.",
            "done": True,
        }
    return {"route": "answer_direct"}


def answer_direct(state: AskAgentState) -> dict[str, Any]:
    question = state.get("question", "")
    history = state.get("history") or []
    session = _ensure_session(state)
    chat_history = format_chat_history_block(history, max_turns=3)
    prompt = format_general_ask_inference(question, chat_history=chat_history)
    answer = sanitize_ask_response(
        _ask_generate(prompt, max_new_tokens=ASK_ANSWER_MAX_TOKENS)
    )
    session["state"] = STATE_QA
    return {
        "answer": answer,
        "session_state": session,
        "done": True,
        "status": answer,
        "statuses": ["Answering from model knowledge..."],
    }


def validate_repo(state: AskAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    root = (session.get("repo_root") or "").strip()
    try:
        resolve_repo_root(root)
    except FileNotFoundError:
        return {
            "error": f"Repo path not found: `{root}`",
            "answer": f"Repo path not found: `{root}`",
            "done": True,
        }
    question = state.get("question", "") or _default_question()
    return {"question": question, "session_state": session}


def plan_query(state: AskAgentState) -> dict[str, Any]:
    question = state.get("question", "")
    history = state.get("history") or []
    session = _ensure_session(state)
    plan = apply_plan_heuristics(_plan_ask_query(question, history), question)
    session["ask_plan"] = {
        "intent_summary": plan.intent_summary,
        "retrieval_query": plan.retrieval_query,
        "answer_mode": plan.answer_mode,
    }
    file_refs = extract_file_refs(question)
    doc_refs = extract_doc_file_refs(question)
    active_files = session.get("active_files") or []
    has_file_target = bool(file_refs) or bool(active_files)
    route = "retrieve"
    if has_file_target and plan.answer_mode != ANSWER_MODE_CLARIFY:
        route = "file_sources"
    return {
        "plan": {
            "intent_summary": plan.intent_summary,
            "retrieval_query": plan.retrieval_query,
            "answer_mode": plan.answer_mode,
            "needs_repo_inventory": plan.needs_repo_inventory,
            "is_follow_up": plan.is_follow_up,
        },
        "session_state": session,
        "route": route,
        "overview": is_overview_question(question),
        "retrieval_refs": file_refs + doc_refs,
    }


def load_file_sources(state: AskAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    root = session.get("repo_root", "")
    question = state.get("question", "")
    max_files = state.get("max_files", 20)
    active_files = session.get("active_files") or []
    sources, files, err = load_context_sources(
        root,
        question,
        active_files,
        max_files=max_files,
        extensions=ASK_FILE_EXTENSIONS,
    )
    if err:
        return {"error": err, "answer": err, "done": True}
    set_active_files(session, root, files)
    session["file_index"] = files
    session["sources_cache"] = sources
    session["sources_from_rag"] = False
    session["state"] = STATE_QA
    status = f"Reading {len(sources)} file(s)... generating answer."
    return {
        "sources": sources,
        "files": files,
        "from_rag": False,
        "session_state": session,
        "statuses": ["Analyzing selected files...", status],
    }


def retrieve_sources(state: AskAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    root = session.get("repo_root", "")
    question = state.get("question", "")
    plan = _plan_from_dict(state.get("plan"), question)
    history = state.get("history") or []
    max_files = state.get("max_files", 20)
    rag_top_k = state.get("rag_top_k", 5)
    overview = bool(state.get("overview"))
    retrieval_refs = state.get("retrieval_refs") or []
    retrieval_query = build_retrieval_query(question, history, plan)

    statuses: list[str] = []
    sources: list[dict[str, str]] = []
    files: list[str] = []
    from_rag = False
    err: str | None = None

    if plan.answer_mode == ANSWER_MODE_CLARIFY:
        cached = session.get("sources_cache") or []
        if cached:
            sources = cached
            files = session.get("file_index") or []
            from_rag = bool(session.get("sources_from_rag"))
            statuses.append("Restating previous answer...")
        elif _rag_index_exists(root):
            statuses.append("Searching repository using RAG...")
            sources, files, from_rag, err = _retrieve_sources_impl(
                root,
                retrieval_query,
                max_files,
                rag_top_k,
                overview=overview,
                file_refs=retrieval_refs,
            )
        else:
            sources, files, err = load_context_sources(
                root, question, [], max_files=max_files
            )
    elif _rag_index_exists(root):
        statuses.append("Searching repository using RAG...")
        sources, files, from_rag, err = _retrieve_sources_impl(
            root,
            retrieval_query,
            max_files,
            rag_top_k,
            overview=overview,
            file_refs=retrieval_refs,
        )
    else:
        sources, files, err = load_context_sources(root, question, [], max_files=max_files)
        statuses.append(
            "No RAG index for this repo (scanning files instead). "
            "Build one with: `python scripts/build_repo_index.py --repo-root <path>`"
        )

    if err:
        return {"error": err, "answer": err, "done": True, "statuses": statuses}
    if not sources:
        msg = (
            "I couldn't find relevant code for that question. "
            "Try rephrasing or rebuild the RAG index for this repo."
        )
        return {"error": msg, "answer": msg, "done": True, "statuses": statuses}

    session["file_index"] = files
    session["sources_cache"] = sources
    session["sources_from_rag"] = from_rag
    session["state"] = STATE_QA
    status = (
        f"Reading {len(sources)} retrieved chunk(s)... generating answer."
        if from_rag
        else f"Reading {len(sources)} file(s)... generating answer."
    )
    statuses.append(status)
    return {
        "sources": sources,
        "files": files,
        "from_rag": from_rag,
        "session_state": session,
        "statuses": statuses,
    }


def prepare_answer(state: AskAgentState) -> dict[str, Any]:
    question = state.get("question", "")
    plan = _plan_from_dict(state.get("plan"), question)
    sources = state.get("sources") or []
    focused = trim_sources_for_prompt(sources)
    if not focused:
        msg = (
            "I couldn't find relevant code for that question. "
            "Try rephrasing or rebuild the RAG index for this repo."
        )
        return {"error": msg, "answer": msg, "done": True}
    mode: str = "unified"
    if not _use_unified_answer(plan, focused):
        mode = "per_file"
    return {
        "sources": focused,
        "answer_mode": mode,
        "file_index": 0,
        "sections": [],
    }


def generate_unified_answer(state: AskAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    root = session.get("repo_root", "")
    question = state.get("question", "")
    history = state.get("history") or []
    plan = _plan_from_dict(state.get("plan"), question)
    focused = state.get("sources") or []
    from_rag = bool(state.get("from_rag"))

    chat_history = format_chat_history_block(history, max_turns=3)
    doc_question = question.strip()
    if plan.answer_mode == ANSWER_MODE_CLARIFY:
        doc_question = (
            f"The user did not understand the previous answer. "
            f"Restate it more simply. Original message: {question.strip()}"
        )
    elif from_rag:
        doc_question = question.strip() + _overview_question_hint()

    inventory_mode = (
        plan.answer_mode == ANSWER_MODE_INVENTORY or plan.needs_repo_inventory
    ) and is_explicit_inventory_request(question)
    intent_summary = plan.intent_summary or question.strip()
    file_list = ", ".join(s["name"] for s in focused)

    if inventory_mode:
        inventory_text, inventory_count = _repo_inventory_block(root)
        prompt = format_repo_inventory_ask_inference(
            repo_root=root,
            file_list=file_list,
            sources=format_sources_block(focused, for_doc=True),
            question=doc_question,
            repo_inventory=inventory_text,
            inventory_count=inventory_count,
            chat_history=chat_history,
            intent_summary=intent_summary,
        )
    else:
        single_file = len(focused) == 1 and not from_rag
        if single_file:
            prompt = format_file_ask_inference(
                repo_root=root,
                file_name=focused[0]["name"],
                source=format_sources_block(focused, for_doc=True),
                question=doc_question,
                intent_summary=intent_summary,
            )
        else:
            prompt = format_folder_ask_inference(
                repo_root=root,
                file_list=file_list,
                sources=format_sources_block(focused, for_doc=True),
                question=doc_question,
                chat_history=chat_history,
                intent_summary=intent_summary,
            )

    answer = sanitize_ask_response(
        _ask_generate(prompt, max_new_tokens=ASK_ANSWER_MAX_TOKENS)
    )
    answer = _prepend_context_block(answer, focused, from_rag=from_rag)
    if inventory_mode:
        inventory_text, inventory_count = _repo_inventory_block(root)
        answer = (
            f"**Repo inventory ({inventory_count} files):**\n"
            f"{inventory_text}\n\n{answer}"
        )
    return {
        "answer": answer,
        "done": True,
        "session_state": session,
        "statuses": ["Generating answer from retrieved context..."],
    }


def init_per_file_answer(state: AskAgentState) -> dict[str, Any]:
    focused = state.get("sources") or []
    from_rag = bool(state.get("from_rag"))
    scores = [
        float(s.get("rag_score", 0))
        for s in focused
        if s.get("rag_score") is not None
    ]
    sections = [
        _context_header(len(focused), from_rag, scores or None),
        *_format_source_listing(focused, from_rag),
        "",
    ]
    return {"sections": sections, "file_index": 0}


def answer_one_file(state: AskAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    root = session.get("repo_root", "")
    question = state.get("question", "")
    plan = _plan_from_dict(state.get("plan"), question)
    focused = state.get("sources") or []
    index = int(state.get("file_index") or 0)
    sections = list(state.get("sections") or [])
    total = len(focused)
    intent_summary = plan.intent_summary or question.strip()

    source = focused[index]
    file_question = _question_for_file(
        question, source["name"], index + 1, total, intent_summary=intent_summary
    )
    prompt = format_file_ask_inference(
        repo_root=root,
        file_name=source["name"],
        source=format_sources_block([source], for_doc=True),
        question=file_question,
        intent_summary=intent_summary,
    )
    section = sanitize_ask_response(
        _ask_generate(prompt, max_new_tokens=ASK_ANSWER_MAX_TOKENS)
    )
    sections.append(f"### {Path(source['name']).name}\n{section}")
    return {
        "sections": sections,
        "file_index": index + 1,
        "status": f"Explaining file {index + 1}/{total}: `{source['name']}`...",
    }


def finalize_per_file_answer(state: AskAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    sections = state.get("sections") or []
    return {
        "answer": "\n".join(sections),
        "done": True,
        "session_state": session,
    }


def route_after_detect(state: AskAgentState) -> str:
    task = state.get("task", "explain")
    if task in ("gen_python", "gen_java"):
        return "gen_code"
    root = (_ensure_session(state).get("repo_root") or "").strip()
    if not root:
        return "no_repo"
    return "validate_repo"


def route_after_no_repo(state: AskAgentState) -> str:
    return str(state.get("route", "answer_direct"))


def route_after_plan(state: AskAgentState) -> str:
    return str(state.get("route", "retrieve"))


def route_after_prepare(state: AskAgentState) -> str:
    if state.get("done"):
        return "end"
    mode = state.get("answer_mode", "unified")
    if mode == "per_file":
        return "per_file"
    return "unified"


def route_after_file(state: AskAgentState) -> str:
    index = int(state.get("file_index") or 0)
    total = len(state.get("sources") or [])
    if index < total:
        return "next_file"
    return "finalize"


# Re-export for repo_ask_chat backward compatibility
__all__ = [
    "sanitize_ask_response",
    "is_repo_scoped_question",
    "STATE_INIT",
    "STATE_QA",
    "ASK_ANSWER_MAX_TOKENS",
]
