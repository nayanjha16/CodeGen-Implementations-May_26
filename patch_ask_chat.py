import re

with open("agent/repo_ask_chat.py", "r") as f:
    content = f.read()

# Add import
import_statement = "from inference.repo_rag_pipeline import RepoRAGPipeline, INDEX_DIR\n"
content = content.replace("from agent.llms import codegen_generate", import_statement + "from agent.llms import codegen_generate")

# Find the general repo analysis part (around line 261)
old_code = """    sources, files, err = load_context_sources(root, question, [], max_files=max_files)
    if err:
        update_last_bot(history, err)
        yield yield_chat(history, {"session_state": session_state})
        return"""

new_code = """    # Try to use RAG if index exists
    rag_index_dir = INDEX_DIR / Path(root).name
    if (rag_index_dir / "faiss.index").exists():
        update_last_bot(history, "Searching repository using RAG...")
        yield yield_chat(history, {"session_state": session_state})
        
        pipeline = RepoRAGPipeline(repo_root=root)
        top_chunks = pipeline.retrieve(question, top_k=5)
        
        if top_chunks:
            sources = []
            files = []
            for chunk in top_chunks:
                meta = chunk["metadata"]
                # Convert chunk to a source dictionary similar to what read_repo_sources returns
                sources.append({
                    "path": meta.get("file_path", ""),
                    "name": meta.get("file_path", ""),
                    "language": "python" if meta.get("file_path", "").endswith(".py") else "java",
                    "snippet": chunk["content"],
                    "ast_summary": f"RAG matched chunk ({meta.get('type')} {meta.get('name', '')})",
                })
                if meta.get("file_path") not in files:
                    files.append(meta.get("file_path"))
            err = None
        else:
            sources, files, err = load_context_sources(root, question, [], max_files=max_files)
    else:
        sources, files, err = load_context_sources(root, question, [], max_files=max_files)

    if err:
        update_last_bot(history, err)
        yield yield_chat(history, {"session_state": session_state})
        return"""

content = content.replace(old_code, new_code)

with open("agent/repo_ask_chat.py", "w") as f:
    f.write(content)

print("Patched agent/repo_ask_chat.py successfully")
