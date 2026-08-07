import ast
import re
from pathlib import Path
from typing import Dict, List, Any

def chunk_python_code(code: str, file_path: str) -> List[Dict[str, Any]]:
    """Parse Python code and chunk into classes, functions, and module-level code."""
    chunks = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        # Fallback to entire file if syntax is invalid
        return [{"content": code, "metadata": {"file_path": file_path, "type": "file"}}]

    lines = code.splitlines()
    
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            start_line = node.lineno - 1
            end_line = node.end_lineno if node.end_lineno is not None else len(lines)
            chunk_content = "\n".join(lines[start_line:end_line])
            
            chunks.append({
                "content": chunk_content,
                "metadata": {
                    "file_path": file_path,
                    "type": "class" if isinstance(node, ast.ClassDef) else "function",
                    "name": node.name,
                    "start_line": start_line + 1,
                    "end_line": end_line
                }
            })
            
    # Add module-level imports or global code if we don't have enough chunks, 
    # but for simplicity, we mostly care about classes/functions.
    if not chunks and code.strip():
        chunks.append({"content": code, "metadata": {"file_path": file_path, "type": "file"}})
        
    return chunks

def chunk_java_code(code: str, file_path: str) -> List[Dict[str, Any]]:
    """Regex-based Java code chunking into classes and methods."""
    chunks = []
    lines = code.splitlines()
    
    # Very simplistic regex to find class/method starts (heuristic)
    class_pattern = re.compile(r'(?:public|protected|private|static|\s)*class\s+(\w+)')
    method_pattern = re.compile(r'(?:public|protected|private|static|\s)*[\w\<\>\[\]]+\s+(\w+)\s*\([^\)]*\)\s*(?:throws\s+[\w\s,]+)?\s*\{')
    
    current_chunk = []
    current_meta = {"file_path": file_path, "type": "file"}
    start_line = 1
    
    bracket_level = 0
    in_chunk = False
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        if not in_chunk:
            class_match = class_pattern.search(line)
            method_match = method_pattern.search(line)
            
            if class_match or method_match:
                in_chunk = True
                current_chunk = [line]
                bracket_level = line.count('{') - line.count('}')
                current_meta = {
                    "file_path": file_path,
                    "type": "class" if class_match else "method",
                    "name": class_match.group(1) if class_match else method_match.group(1),
                    "start_line": i + 1
                }
                if bracket_level <= 0 and '{' in line_stripped:
                    # Single line method or interface
                    in_chunk = False
                    current_meta["end_line"] = i + 1
                    chunks.append({"content": "\n".join(current_chunk), "metadata": current_meta.copy()})
        else:
            current_chunk.append(line)
            bracket_level += line.count('{') - line.count('}')
            
            if bracket_level <= 0:
                in_chunk = False
                current_meta["end_line"] = i + 1
                chunks.append({"content": "\n".join(current_chunk), "metadata": current_meta.copy()})
                
    if not chunks and code.strip():
         chunks.append({"content": code, "metadata": {"file_path": file_path, "type": "file"}})
         
    return chunks

def _merge_small_sections(
    sections: List[Dict[str, Any]], min_chars: int
) -> List[Dict[str, Any]]:
    """Fold undersized sections into their neighbour.

    Short boilerplate ("License", "Contributing") otherwise wins on cosine
    similarity against a summary query and crowds out the substantive prose.
    """
    merged: List[Dict[str, Any]] = []
    for section in sections:
        if merged and len(merged[-1]["content"]) < min_chars:
            previous = merged[-1]
            previous["content"] = f"{previous['content']}\n\n{section['content']}"
            previous["metadata"]["end_line"] = section["metadata"]["end_line"]
            continue
        merged.append(section)
    # A trailing short section has no successor to absorb it.
    if len(merged) > 1 and len(merged[-1]["content"]) < min_chars:
        tail = merged.pop()
        merged[-1]["content"] = f"{merged[-1]['content']}\n\n{tail['content']}"
        merged[-1]["metadata"]["end_line"] = tail["metadata"]["end_line"]
    return merged


def chunk_markdown_doc(
    file_path: str,
    content: str,
    max_chars: int = 4000,
    min_chars: int = 500,
) -> List[Dict[str, Any]]:
    """Split a markdown document into one chunk per top-level section.

    A single whole-file chunk gets truncated to the embedder's token limit, so
    most of a long README would never be retrievable.
    """
    lines = content.splitlines()
    if not content.strip():
        return []

    name = Path(file_path).name
    sections: List[Dict[str, Any]] = []
    heading = name
    buffer: List[str] = []
    start_line = 1

    def flush(end_line: int) -> None:
        body = "\n".join(buffer).strip()
        if not body:
            return
        # Sections opened by a heading already carry it; a leading preamble
        # needs the filename so the chunk still names its source.
        if not body.startswith("#"):
            body = f"# {heading}\n\n{body}"
        sections.append({
            "content": body[:max_chars],
            "metadata": {
                "file_path": file_path,
                "type": "doc",
                "name": heading,
                "start_line": start_line,
                "end_line": end_line,
            },
        })

    for i, line in enumerate(lines, start=1):
        # Split on level-1/2 headings; deeper headings stay with their parent.
        if re.match(r"^#{1,2}\s+\S", line):
            flush(i - 1)
            heading = line.lstrip("#").strip() or name
            buffer = [line]
            start_line = i
            continue
        buffer.append(line)
    flush(len(lines))

    if not sections:
        return [{
            "content": content[:max_chars],
            "metadata": {"file_path": file_path, "type": "doc", "name": name},
        }]
    return _merge_small_sections(sections, min_chars)


def chunk_code_file(file_path: str, content: str) -> List[Dict[str, Any]]:
    if file_path.endswith('.py'):
        return chunk_python_code(content, file_path)
    elif file_path.endswith('.java'):
        return chunk_java_code(content, file_path)
    else:
        return [{"content": content, "metadata": {"file_path": file_path, "type": "file"}}]
