"""Ask Agent — read-only Q&A over a repo workspace."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Generator

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

from agent.ask_query_planner import (
    ANSWER_MODE_CLARIFY,
    ANSWER_MODE_INVENTORY,
    ANSWER_MODE_PER_FILE,
    AskPlan,
    OVERVIEW_RETRIEVAL_QUERY,
    apply_plan_heuristics,
    build_retrieval_query,
    is_explicit_inventory_request,
    is_overview_question,
    plan_ask_query,
)
from agent.ask_graph import get_ask_graph
from agent.ask_nodes import is_repo_scoped_question, sanitize_ask_response
from agent.ask_state import STATE_INIT, STATE_QA, initial_ask_state
from inference.repo_rag_pipeline import (
    DEFAULT_WEAK_SCORE,
    get_repo_rag_pipeline,
    rag_index_exists,
)
from agent.llms import ask_generate, codegen_generate
from agent.repo_utils import (
    append_bot,
    append_user,
    empty_session,
    extract_doc_file_refs,
    extract_file_refs,
    list_repo_relative_files,
    load_context_sources,
    update_last_bot,
    yield_chat,
)

ASK_ANSWER_MAX_TOKENS = 256
RAG_SCORE_MARGIN = float(os.environ.get("RAG_SCORE_MARGIN", "0.08"))
RAG_OVERVIEW_SCORE_MARGIN = float(os.environ.get("RAG_OVERVIEW_SCORE_MARGIN", "0.15"))
ASK_FILE_EXTENSIONS = ".java,.py,.md"

_sanitize_ask_response = sanitize_ask_response


def _default_question() -> str:
    return "Summarize what this folder contains and explain the main functionality."


def _rag_top_k(rag_top_k: int) -> int:
    return max(1, min(int(rag_top_k), 20))


def _max_chunk_score(chunks: list[dict]) -> float:
    if not chunks:
        return 0.0
    return max(float(chunk.get("score", 0)) for chunk in chunks)


def _chunk_language(rel_path: str) -> str:
    lower = str(rel_path).lower()
    if lower.endswith(".py"):
        return "python"
    if lower.endswith((".md", ".txt", ".rst")):
        return "markdown"
    return "java"


def _sources_from_rag_chunks(chunks: list[dict]) -> tuple[list[dict[str, str]], list[str]]:
    sources: list[dict[str, str]] = []
    files: list[str] = []
    for chunk in chunks:
        meta = chunk.get("metadata") or {}
        rel_path = meta.get("file_path", "")
        score = chunk.get("score")
        start_line = meta.get("start_line")
        end_line = meta.get("end_line")
        sources.append({
            "path": rel_path,
            "name": rel_path,
            "language": _chunk_language(rel_path),
            "snippet": chunk.get("content", ""),
            "ast_summary": f"RAG matched chunk ({meta.get('type')} {meta.get('name', '')})",
            "rag_score": score,
            "chunk_type": str(meta.get("type") or ""),
            "chunk_name": str(meta.get("name") or ""),
            "start_line": str(start_line) if start_line is not None else "",
            "end_line": str(end_line) if end_line is not None else "",
        })
        if rel_path and rel_path not in files:
            files.append(rel_path)
    return sources, files


def _retrieve_sources(
    root: str,
    retrieval_query: str,
    max_files: int,
    rag_top_k: int,
    *,
    overview: bool = False,
    file_refs: list[str] | None = None,
) -> tuple[list[dict[str, str]], list[str], bool, str | None]:
    """Return (sources, files, from_rag, error_message)."""
    if rag_index_exists(root):
        pipeline = get_repo_rag_pipeline(root)
        top_k = _rag_top_k(rag_top_k)
        query = retrieval_query or _default_question()

        file_paths: list[str] | None = None
        if file_refs:
            file_paths = pipeline.resolve_index_paths(list(file_refs)) or None

        retrieve_fn = pipeline.retrieve_overview if overview else pipeline.retrieve
        margin = RAG_OVERVIEW_SCORE_MARGIN if overview else RAG_SCORE_MARGIN
        top_chunks = retrieve_fn(
            query,
            top_k=top_k,
            file_paths=file_paths,
            score_margin=margin,
            path_boost=True,
        )

        can_retry = not file_paths and query != OVERVIEW_RETRIEVAL_QUERY
        if can_retry and top_chunks and _max_chunk_score(top_chunks) < DEFAULT_WEAK_SCORE:
            retry_chunks = pipeline.retrieve_overview(
                OVERVIEW_RETRIEVAL_QUERY,
                top_k=top_k,
            )
            if _max_chunk_score(retry_chunks) > _max_chunk_score(top_chunks):
                top_chunks = retry_chunks

        if not top_chunks:
            return [], [], True, (
                "I couldn't find relevant code for that question in the RAG index. "
                "Try rephrasing or rebuild the index with "
                "`python scripts/build_repo_index.py --repo-root <path>`."
            )

        if _max_chunk_score(top_chunks) < DEFAULT_WEAK_SCORE:
            return [], [], True, (
                "I couldn't find confident matches for that question in the RAG index. "
                "Try rephrasing or rebuild the index with "
                "`python scripts/build_repo_index.py --repo-root <path>`."
            )

        sources, files = _sources_from_rag_chunks(top_chunks)
        return sources, files, True, None
    sources, files, err = load_context_sources(root, retrieval_query, [], max_files=max_files)
    return sources, files, False, err


def _apply_graph_update(
    history: list[dict[str, str]],
    session_state: dict[str, Any],
    update: dict[str, Any],
) -> dict[str, Any] | None:
    if update.get("session_state") is not None:
        session_state.clear()
        session_state.update(update["session_state"])

    extras: dict[str, Any] = {"session_state": session_state}
    if update.get("show_action_buttons"):
        extras["show_action_buttons"] = True

    for status in update.get("statuses") or []:
        if status:
            update_last_bot(history, status)

    status = update.get("status")
    if status:
        update_last_bot(history, status)

    answer = update.get("answer")
    if answer and update.get("done"):
        update_last_bot(history, answer)
        return yield_chat(history, extras)

    if update.get("done") and update.get("error"):
        update_last_bot(history, update["error"])
        return yield_chat(history, extras)

    if status or update.get("statuses"):
        return yield_chat(history, extras)
    return None


def chat_ask_generator(
    user_message: str,
    history: list[dict[str, str]],
    session_state: dict[str, Any],
    repo_root: str,
    max_files: int = 20,
    rag_top_k: int = 5,
) -> Generator[dict[str, Any], None, None]:
    if not session_state:
        session_state = empty_session(repo_root)

    if repo_root:
        session_state["repo_root"] = repo_root

    task = __import__("agent.repo_utils", fromlist=["detect_ask_task"]).detect_ask_task(
        user_message
    )
    append_user(history, user_message)

    if task in ("gen_python", "gen_java"):
        append_bot(history, "Generating code...")
    elif not (session_state.get("repo_root") or repo_root or "").strip():
        if is_repo_scoped_question(user_message.strip()):
            append_bot(history, "Set the **Project root** path above, then ask your question.")
        else:
            append_bot(history, "Answering from model knowledge...")
    else:
        append_bot(history, "Understanding your question...")
    yield yield_chat(history, {"session_state": session_state})

    graph = get_ask_graph()
    state = initial_ask_state(
        user_message,
        history,
        session_state,
        repo_root,
        max_files=max_files,
        rag_top_k=rag_top_k,
    )

    final: dict[str, Any] | None = None
    for event in graph.stream(state, stream_mode="updates"):
        for update in event.values():
            chunk = _apply_graph_update(history, session_state, update)
            if chunk is not None:
                final = chunk
                yield chunk

    if final is None:
        result = graph.invoke(state)
        _apply_graph_update(history, session_state, result)
        yield yield_chat(history, {"session_state": session_state})


def strip_migrate_prefix(question: str) -> str:
    lower = question.lower()
    if lower.startswith("migrate"):
        return question[7:].strip(" :—-")
    return question
