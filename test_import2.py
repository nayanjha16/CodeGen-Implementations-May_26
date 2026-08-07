import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
print("Trying chunking...")
from agent.chunking import chunk_code_file
print("Trying inference.repo_rag_pipeline...")
from inference.repo_rag_pipeline import RepoRAGPipeline
print("Success")
