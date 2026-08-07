import sys
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from pathlib import Path
import json

# Adjust imports
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Let's import the scripts
from scripts.build_repo_index import build_index_for_repo
from inference.repo_rag_pipeline import RepoRAGPipeline

def run_test():
    repo_root = str(PROJECT_ROOT)
    
    print("=== 1. Building Index for this Repository ===")
    print("Calling build_index_for_repo...")
    build_index_for_repo(repo_root)
    
    print("\n=== 2. Querying RAG Pipeline ===")
    pipeline = RepoRAGPipeline(repo_root=repo_root)
    query = "Show me the prompt formatting logic for java2py inference"
    print(f"Query: '{query}'")
    
    results = pipeline.retrieve(query, top_k=3)
    
    print("\n=== 3. Results ===")
    for i, res in enumerate(results, 1):
        meta = res['metadata']
        print(f"\nResult {i} (Score: {res.get('score', 0):.4f}):")
        print(f"File: {meta.get('file_path')}")
        print(f"Type: {meta.get('type')} {meta.get('name', '')}")
        print("-" * 40)
        # print first few lines of content
        content_lines = res['content'].splitlines()
        print("\n".join(content_lines[:10]))
        if len(content_lines) > 10:
            print("...")

if __name__ == "__main__":
    run_test()
