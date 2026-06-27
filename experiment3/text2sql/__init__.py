"""Text-to-SQL multi-LLM benchmark package."""
import os
from pathlib import Path

# Keep all HuggingFace / MLX model downloads inside the project (models/hf-cache)
# instead of the global ~/.cache/huggingface. setdefault lets a shell HF_HOME win.
# Must run before transformers / mlx_lm import huggingface_hub (they load lazily,
# after `import text2sql`), so the cache path is picked up on first model load.
os.environ.setdefault("HF_HOME", str(Path(__file__).resolve().parent.parent / "models" / "hf-cache"))

__version__ = "0.1.0"
