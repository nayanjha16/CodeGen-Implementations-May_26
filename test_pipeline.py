import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
from inference.repo_rag_pipeline import RepoRAGPipeline

print("Starting pipeline init...", flush=True)
pipeline = RepoRAGPipeline(repo_root=str(PROJECT_ROOT), device="cpu")
print("Instantiated pipeline", flush=True)
