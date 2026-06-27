import json
import subprocess
import sys
from pathlib import Path

class MLXTrainer:
    """LoRA fine-tuning via the mlx_lm.lora CLI.

    text_format: when True, rewrite the {prompt, completion} rows into mlx's "text"
    format ({"text": prompt+completion}) instead of "completions" format. The
    completions path calls tokenizer.apply_chat_template, which crashes for models
    whose tokenizer has no chat_template (e.g. Codestral-22B-v0.1). "text" tokenizes
    raw — and matches the raw-prompt inference those models already use.
    """

    def __init__(self, repo: str, lora_rank: int = 16, iters: int = 600,
                 batch_size: int = 4, learning_rate: float = 2e-4, text_format: bool = False):
        self.repo = repo
        self.lora_rank = lora_rank
        self.iters = iters
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.text_format = text_format

    def _write_data(self, src: Path, dst: Path) -> None:
        if not self.text_format:
            dst.write_bytes(Path(src).read_bytes())
            return
        rows = [json.loads(l) for l in Path(src).read_text().splitlines() if l.strip()]
        with dst.open("w") as f:
            for r in rows:
                f.write(json.dumps({"text": r["prompt"] + r["completion"]}) + "\n")

    def train(self, train_jsonl: Path, valid_jsonl: Path, adapter_out: Path) -> Path:
        """Runs mlx_lm.lora. mlx expects a data dir with train.jsonl/valid.jsonl."""
        data_dir = Path(adapter_out).parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        self._write_data(Path(train_jsonl), data_dir / "train.jsonl")
        self._write_data(Path(valid_jsonl), data_dir / "valid.jsonl")
        cmd = [
            sys.executable, "-m", "mlx_lm.lora",  # the venv python (mlx_lm lives there), not system "python"
            "--model", self.repo, "--train",
            "--data", str(data_dir),
            "--adapter-path", str(adapter_out),
            "--iters", str(self.iters),
            "--batch-size", str(self.batch_size),
            "--num-layers", "16",
            "--learning-rate", str(self.learning_rate),
        ]
        subprocess.run(cmd, check=True)
        return Path(adapter_out)
