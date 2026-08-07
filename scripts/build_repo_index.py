import argparse
import sys
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agent.chunking import chunk_code_file, chunk_markdown_doc
from inference.repo_rag_pipeline import RepoRAGPipeline, repo_index_dir

SKIP_DIRS = {"venv", "node_modules", "data", "deploy", "models", "__pycache__"}
DOC_EXTENSIONS = {".md", ".txt", ".rst"}
CODE_EXTENSIONS = {".py", ".java"}


def _should_skip_path(file_path: Path) -> bool:
    parts = file_path.parts
    if any(part.startswith(".") for part in parts) and ".github" not in str(file_path):
        return True
    return any(part in SKIP_DIRS for part in parts)


def _file_summary_chunk(rel_path: str, content: str) -> dict | None:
    lines = content.splitlines()
    if not lines:
        return None
    preview = "\n".join(lines[:20])
    names: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("class ") or stripped.startswith("def "):
            names.append(stripped.split("(")[0].replace("class ", "").replace("def ", ""))
        if " class " in stripped or stripped.startswith("public class"):
            token = stripped.split("class ", 1)[-1].split()[0].split("{")[0]
            if token:
                names.append(token)
    summary_names = ", ".join(names[:12]) if names else "(no symbols detected)"
    return {
        "content": f"File overview for {rel_path}.\nSymbols: {summary_names}\n\n{preview}",
        "metadata": {
            "file_path": rel_path,
            "type": "summary",
            "name": Path(rel_path).name,
        },
    }



def _should_skip_file(file_path: Path) -> bool:
    """Skip .py stubs when a sibling .java file exists at the same path."""
    if file_path.suffix.lower() != ".py":
        return False
    return file_path.with_suffix(".java").exists()


def build_index_for_repo(repo_root: str, include_tests: bool = True):
    root_path = Path(repo_root).resolve()
    if not root_path.exists():
        print(f"Error: Repository {repo_root} does not exist.")
        return

    print(f"Scanning repository: {root_path}")

    all_chunks = []

    for file_path in root_path.rglob("*"):
        if not file_path.is_file():
            continue
        if _should_skip_path(file_path):
            continue
        if _should_skip_file(file_path):
            continue

        suffix = file_path.suffix.lower()
        # Index every doc, not just README: questions name files like ROADMAP.md
        # too, and an unindexed doc silently retrieves unrelated code instead.
        is_doc = suffix in DOC_EXTENSIONS
        is_code = suffix in CODE_EXTENSIONS
        is_test = "test" in file_path.parts or file_path.name.endswith("Test.java")

        if not is_doc and not is_code:
            continue
        if is_test and not include_tests:
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
            rel_path = str(file_path.relative_to(root_path))
            if is_doc:
                all_chunks.extend(chunk_markdown_doc(rel_path, content))
                continue

            summary = _file_summary_chunk(rel_path, content)
            if summary:
                all_chunks.append(summary)

            chunks = chunk_code_file(rel_path, content)
            for chunk in chunks:
                meta = chunk.get("metadata") or {}
                if is_test:
                    meta = {**meta, "type": "test"}
                chunk["metadata"] = meta
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"Warning: Could not process {file_path}: {e}")

    print(f"Extracted {len(all_chunks)} chunks from {repo_root}")
    print(f"Index will be saved under: {repo_index_dir(str(root_path))}")

    pipeline = RepoRAGPipeline(repo_root=str(root_path))
    pipeline.build_index(all_chunks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build FAISS RAG index for a repository")
    parser.add_argument("--repo-root", type=str, required=True, help="Path to the repository root")
    parser.add_argument(
        "--no-tests",
        action="store_true",
        help="Exclude test files from the index",
    )
    args = parser.parse_args()

    build_index_for_repo(args.repo_root, include_tests=not args.no_tests)
