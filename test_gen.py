import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
print("Before import")
from inference.generator import resolve_codegen_model_id
print("After import")
