import json
import logging
from pathlib import Path
from typing import Any, Dict, Generator

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

logger = logging.getLogger(__name__)


def _trace(step: str, detail: str) -> dict[str, str]:
    return {"step": step, "detail": detail}


def _merge(state: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    traces = list(state.get("trace") or []) + list(update.get("trace") or [])
    merged = {**state, **update, "trace": traces}
    return merged


def iter_migrate_java_path(
    path: str,
    max_files: int = 5,
    max_retries: int = 3
) -> Generator[Dict[str, Any], None, None]:
    """
    Generator that migrates Java files to Python with full agentic dependency resolution,
    validation, and self-correction. Yields state snapshots.
    """
    root = Path(path)
    state = {
        "status": f"Resolving files in {path}...",
        "current_java_path": "",
        "java_code": "",
        "python_code": "",
        "written_paths": [],
        "trace": [_trace("init", f"Target path: {path}")],
        "error": ""
    }
    yield state

    # Step 1: List java files
    list_result_raw = list_java_files.invoke({"path": path, "recursive": True, "max_files": max_files})
    try:
        list_result = json.loads(list_result_raw)
    except Exception:
        list_result = {"files": [], "error": str(list_result_raw)}
        
    if "error" in list_result:
        state["error"] = list_result["error"]
        state["status"] = "Failed to resolve path."
        yield state
        return

    java_files = list_result.get("files", [])
    if not java_files:
        state["status"] = "No .java files found."
        state["trace"].append(_trace("list", "No .java files resolved."))
        yield state
        return

    state["trace"].append(_trace("list", f"Found {len(java_files)} files to convert."))
    
    # Process each file
    written_paths = []
    
    for i, jf_path in enumerate(java_files):
        jf_p = Path(jf_path)
        status_prefix = f"Converting {i+1}/{len(java_files)}: {jf_p.name}..."
        state["status"] = status_prefix
        state["current_java_path"] = jf_path
        state["java_code"] = ""
        state["python_code"] = ""
        yield state
        
        # Read java file
        java_code = read_text_file.invoke({"path": jf_path})
        if java_code.startswith("(missing file:"):
            state["trace"].append(_trace("read_error", f"Could not read {jf_path}"))
            continue
            
        state["java_code"] = java_code
        state["trace"].append(_trace("read", f"Read {jf_p.name} ({len(java_code)} chars)"))
        yield state
        
        # Find dependencies
        state["status"] = f"{status_prefix} Finding dependencies..."
        yield state
        
        deps_raw = find_local_java_dependencies.invoke({
            "java_code": java_code,
            "repo_root": str(root if root.is_dir() else root.parent)
        })
        deps = json.loads(deps_raw).get("dependencies", [])
        
        deps_context = ""
        if deps:
            state["trace"].append(_trace("find_deps", f"Found {len(deps)} local dependencies."))
            yield state
            
            for dep_path in deps:
                if dep_path == jf_path:
                    continue
                dep_code = read_text_file.invoke({"path": dep_path})
                if not dep_code.startswith("(missing"):
                    dep_name = Path(dep_path).name
                    state["trace"].append(_trace("read_dep", f"Read dependency: {dep_name}"))
                    deps_context += f"\n// Dependency context: {dep_name}\n{dep_code}\n"
            yield state
            
        # Convert
        state["status"] = f"{status_prefix} Generating Python..."
        yield state
        
        prompt = format_java2py_inference(java_code, few_shot=deps_context)
        python_code = codegen_generate(prompt)
        
        state["python_code"] = python_code
        state["trace"].append(_trace("generate", f"Generated {len(python_code)} chars of Python"))
        yield state
        
        # Validation & Fix Loop
        attempts = 0
        while attempts <= max_retries:
            attempts += 1
            state["status"] = f"{status_prefix} Validating (Attempt {attempts}/{max_retries+1})..."
            yield state
            
            val_res = validate_python_code.invoke({"code": python_code})
            if val_res == "OK":
                state["trace"].append(_trace("validate", f"Validation passed on attempt {attempts}"))
                break
                
            state["trace"].append(_trace("validate_fail", val_res[:100] + "..."))
            
            if attempts > max_retries:
                state["trace"].append(_trace("validate", "Max retries reached. Keeping last version."))
                break
                
            # Self-correct
            state["status"] = f"{status_prefix} Fixing validation errors..."
            yield state
            
            fix_state = dict(initial_state(
                f"Fix the python code. The original java was:\n{java_code}\nValidation error:\n{val_res}",
                unit="auto"
            ))
            fix_state["python_code"] = python_code
            fix_state["stderr"] = val_res
            
            fix_state = _merge(fix_state, attach_ast(fix_state))
            fix_state = _merge(fix_state, fix_python(fix_state))
            
            python_code = fix_state.get("python_code") or python_code
            state["python_code"] = python_code
            
            for t in fix_state.get("trace", []):
                state["trace"].append(t)
            yield state
            
        # Write (with comments)
        from agent.repo_utils import add_python_comments

        python_code = add_python_comments(python_code)
        out_path = jf_p.with_suffix(".py")
        write_res = write_text_file.invoke({"path": str(out_path), "content": python_code})
        state["trace"].append(_trace("write", write_res))
        
        written_paths.append(str(out_path))
        state["written_paths"] = list(written_paths)
        
        state["status"] = f"Finished {jf_p.name}"
        yield state

    state["status"] = f"Done! Migrated {len(written_paths)} files."
    state["trace"].append(_trace("done", f"Total files written: {len(written_paths)}"))
    yield state


def run_migrate_java_path(
    path: str,
    max_files: int = 5,
    max_retries: int = 3
) -> Dict[str, Any]:
    """Non-streaming wrapper for API/tests."""
    last_state = None
    for state in iter_migrate_java_path(path, max_files, max_retries):
        last_state = state
    return last_state or {}
