import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Generator, List, Tuple

from agent.tools import (
    find_local_java_dependencies,
    list_java_files,
    read_text_file,
    validate_python_code,
    write_text_file,
)
from agent.llms import codegen_generate
from data.scripts.prompt_templates import format_java2py_inference
from agent.state import initial_state
from agent.nodes import attach_ast, fix_python
from agent.repo_migrate import _trace, _merge

logger = logging.getLogger(__name__)

# States for the conversational agent
STATE_INIT = "init"
STATE_ASK_DEPS = "ask_deps"
STATE_CONVERTING = "converting"
STATE_REVIEW_PROMPT = "review_prompt"
STATE_DONE = "done"

def _yield_chat(history: List[Dict[str, str]], state: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to clone state and attach history for UI updates."""
    s = dict(state)
    s["history"] = list(history)
    return s

def _append_user(history: List[Dict[str, str]], content: str) -> None:
    history.append({"role": "user", "content": content})

def _append_bot(history: List[Dict[str, str]], content: str) -> None:
    history.append({"role": "assistant", "content": content})

def _update_last_bot(history: List[Dict[str, str]], content: str) -> None:
    if history and history[-1]["role"] == "assistant":
        history[-1]["content"] = content
    else:
        _append_bot(history, content)

def chat_migrate_generator(
    user_message: str,
    history: List[Dict[str, str]],
    session_state: Dict[str, Any],
    max_retries: int = 3
) -> Generator[Dict[str, Any], None, None]:
    """
    State machine generator for the Gradio Chatbot.
    Yields dicts with {"history": [...], "session_state": {...}, "review_files": [...]}
    """
    if not session_state:
        session_state = {
            "state": STATE_INIT,
            "target_path": "",
            "pending_files": [],
            "deps_found": [],
            "written_files": [],
            "traces": [],
            "file_contents": [] # [{path, java, python}] for review
        }
    
    current_state = session_state.get("state", STATE_INIT)
    
    # -------------------------------------------------------------
    # STATE: INIT (Looking for a path to convert)
    # -------------------------------------------------------------
    if current_state in (STATE_INIT, STATE_DONE):
        # Reset session
        session_state = {
            "state": STATE_INIT, "target_path": "", "pending_files": [], 
            "deps_found": [], "written_files": [], "traces": [], "file_contents": []
        }
        path = user_message.strip()
        
        # Echo user
        _append_user(history, user_message)
        _append_bot(history, "Analyzing path...")
        yield _yield_chat(history, {"session_state": session_state})
        
        root = Path(path)
        if not root.exists():
            _update_last_bot(history, f"❌ I could not find the path: `{path}`. Please provide a valid file or folder path.")
            yield _yield_chat(history, {"session_state": session_state})
            return
            
        session_state["target_path"] = path
        
        # Resolve files
        list_result_raw = list_java_files.invoke({"path": path, "recursive": True, "max_files": 20})
        try:
            list_result = json.loads(list_result_raw)
        except Exception:
            list_result = {"files": []}
            
        java_files = list_result.get("files", [])
        if not java_files:
            _update_last_bot(history, f"❌ No `.java` files found in `{path}`.")
            yield _yield_chat(history, {"session_state": session_state})
            return
            
        session_state["pending_files"] = java_files
        _update_last_bot(history, f"🔍 Found {len(java_files)} target `.java` file(s). Checking for dependencies...")
        yield _yield_chat(history, {"session_state": session_state})
        
        # Check direct dependencies of the targets
        all_deps = set()
        repo_root = str(root if root.is_dir() else root.parent)
        
        for jf in java_files:
            java_code = read_text_file.invoke({"path": jf})
            if not java_code.startswith("(missing"):
                deps_raw = find_local_java_dependencies.invoke({"java_code": java_code, "repo_root": repo_root})
                deps = json.loads(deps_raw).get("dependencies", [])
                for d in deps:
                    if d not in java_files: # don't count if it's already a target
                        all_deps.add(d)
        
        all_deps = list(all_deps)
        session_state["deps_found"] = all_deps
        
        if all_deps:
            session_state["state"] = STATE_ASK_DEPS
            deps_list = "\n".join([f"- `{Path(d).name}`" for d in all_deps[:5]])
            if len(all_deps) > 5:
                deps_list += f"\n- ...and {len(all_deps)-5} more."
                
            _update_last_bot(history, f"I found the target file(s). However, they depend on **{len(all_deps)} direct local dependencies**:\n{deps_list}\n\n**Would you like me to convert these dependencies as well?** (Reply Yes/No)")
            yield _yield_chat(history, {"session_state": session_state})
            return
        else:
            # No deps found, proceed directly to conversion
            session_state["state"] = STATE_CONVERTING
            _append_bot(history, "No external local dependencies found. Starting conversion...")
            yield _yield_chat(history, {"session_state": session_state})
            # Flow falls through to STATE_CONVERTING
            current_state = STATE_CONVERTING

    # -------------------------------------------------------------
    # STATE: ASK DEPS (Waiting for Yes/No)
    # -------------------------------------------------------------
    if current_state == STATE_ASK_DEPS:
        ans = user_message.strip().lower()
        _append_user(history, user_message)
        _append_bot(history, "Understood. Preparing file list...")
        yield _yield_chat(history, {"session_state": session_state})
        
        if ans in ("yes", "y", "sure", "ok", "convert"):
            session_state["pending_files"].extend(session_state["deps_found"])
            _update_last_bot(history, f"Added {len(session_state['deps_found'])} dependencies. Starting conversion of {len(session_state['pending_files'])} files...")
        else:
            _update_last_bot(history, f"Skipping dependencies. Starting conversion of {len(session_state['pending_files'])} target file(s)...")
            
        session_state["state"] = STATE_CONVERTING
        yield _yield_chat(history, {"session_state": session_state})
        current_state = STATE_CONVERTING

    # -------------------------------------------------------------
    # STATE: CONVERTING (Loop through pending files)
    # -------------------------------------------------------------
    if current_state == STATE_CONVERTING:
        files_to_convert = session_state.get("pending_files", [])
        written_files = session_state.get("written_files", [])
        file_contents = session_state.get("file_contents", [])
        
        for i, jf_path in enumerate(files_to_convert):
            jf_p = Path(jf_path)
            
            # Start UI stream for this file
            msg_prefix = f"⏳ **({i+1}/{len(files_to_convert)})** `{jf_p.name}`: "
            _append_bot(history, msg_prefix + "Reading...")
            yield _yield_chat(history, {"session_state": session_state})
            
            java_code = read_text_file.invoke({"path": jf_path})
            if java_code.startswith("(missing"):
                _update_last_bot(history, msg_prefix + "❌ File missing, skipped.")
                yield _yield_chat(history, {"session_state": session_state})
                continue
                
            # Get deps for context (even if we aren't converting them, we need them for context)
            _update_last_bot(history, msg_prefix + "Generating Python...")
            yield _yield_chat(history, {"session_state": session_state})
            
            deps_raw = find_local_java_dependencies.invoke({
                "java_code": java_code,
                "repo_root": str(jf_p.parent) # approx root
            })
            deps = json.loads(deps_raw).get("dependencies", [])
            deps_context = ""
            for dep_path in deps:
                if dep_path != jf_path:
                    dep_code = read_text_file.invoke({"path": dep_path})
                    if not dep_code.startswith("(missing"):
                        deps_context += f"\n// Dependency context: {Path(dep_path).name}\n{dep_code}\n"
            
            # Generate
            prompt = format_java2py_inference(java_code, few_shot=deps_context)
            python_code = codegen_generate(prompt)
            
            # Validate & Fix
            _update_last_bot(history, msg_prefix + "Validating...")
            yield _yield_chat(history, {"session_state": session_state})
            
            attempts = 0
            while attempts <= max_retries:
                attempts += 1
                val_res = validate_python_code.invoke({"code": python_code})
                if val_res == "OK":
                    break
                    
                if attempts > max_retries:
                    break
                    
                _update_last_bot(history, msg_prefix + f"Fixing validation errors (Attempt {attempts})...")
                yield _yield_chat(history, {"session_state": session_state})
                
                fix_state = dict(initial_state(
                    f"Fix the python code. Original java:\n{java_code}\nError:\n{val_res}",
                    unit="auto"
                ))
                fix_state["python_code"] = python_code
                fix_state["stderr"] = val_res
                fix_state["attempts"] = attempts - 1
                fix_state["max_retries"] = max_retries
                fix_state = _merge(fix_state, attach_ast(fix_state))
                fix_state = _merge(fix_state, fix_python(fix_state))
                python_code = fix_state.get("python_code") or python_code
            
            # Write
            _update_last_bot(history, msg_prefix + "Writing to disk...")
            yield _yield_chat(history, {"session_state": session_state})
            
            out_path = jf_p.with_suffix(".py")
            write_text_file.invoke({"path": str(out_path), "content": python_code})
            
            written_files.append(str(out_path))
            file_contents.append({
                "name": jf_p.name,
                "path": str(out_path),
                "java": java_code,
                "python": python_code
            })
            session_state["written_files"] = written_files
            session_state["file_contents"] = file_contents
            
            _update_last_bot(history, msg_prefix + "✅ Done.")
            yield _yield_chat(history, {"session_state": session_state})
            
        session_state["written_files"] = written_files
        session_state["file_contents"] = file_contents
        
        session_state["state"] = STATE_REVIEW_PROMPT
        _append_bot(history, f"🎉 **Conversion complete!** Generated {len(written_files)} `.py` file(s).\n\nUse the buttons below to Review the code, Keep the files, or Undo (delete them).")
        
        yield _yield_chat(history, {
            "session_state": session_state,
            "show_action_buttons": True
        })
        current_state = STATE_REVIEW_PROMPT

def chat_action_undo(session_state: Dict[str, Any], history: List[Dict[str, str]]) -> Dict[str, Any]:
    """Delete the generated files."""
    written = session_state.get("written_files", [])
    deleted = 0
    for p in written:
        try:
            Path(p).unlink(missing_ok=True)
            deleted += 1
        except Exception as e:
            logger.error(f"Failed to delete {p}: {e}")
            
    _append_bot(history, f"🗑️ **Undone.** Deleted {deleted} generated `.py` file(s).")
    session_state["state"] = STATE_INIT
    return _yield_chat(history, {"session_state": session_state, "show_action_buttons": False, "review_data": []})

def chat_action_keep(session_state: Dict[str, Any], history: List[Dict[str, str]]) -> Dict[str, Any]:
    """Keep the files and close session."""
    _append_bot(history, "💾 **Kept.** Files remain on disk. You can provide a new path to convert more.")
    session_state["state"] = STATE_INIT
    return _yield_chat(history, {"session_state": session_state, "show_action_buttons": False, "review_data": []})

def chat_action_review(session_state: Dict[str, Any], history: List[Dict[str, str]]) -> Dict[str, Any]:
    """Trigger the review accordion UI."""
    _append_bot(history, "👀 **Reviewing code.** Check the expandable sections below.")
    # Stay in review state, but hide action buttons and send review data
    return _yield_chat(history, {
        "session_state": session_state, 
        "show_action_buttons": True,
        "review_data": session_state.get("file_contents", [])
    })
