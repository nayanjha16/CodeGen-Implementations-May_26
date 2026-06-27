"""Canary the two NEW LoRA trainer paths cheaply before the 15-adapter run.

Stage C only validated the HF-causal path (codegen). This proves, with tiny data
and minimal iters/epochs, that:
  - Seq2SeqTrainer (CodeT5+)  trains -> saves a PEFT adapter -> reloads + generates.
  - MLXTrainer (sys.executable fix) invokes mlx_lm.lora -> saves an adapter -> reloads.

Run ONE path at a time (single Apple GPU):
    python scripts/canary_trainers.py seq2seq
    python scripts/canary_trainers.py mlx
"""
import sys
from pathlib import Path
from text2sql.finetune.orchestrator import prepare_finetune_data

SPIDER = "data/spider/spider_data"
BIRD = "data/bird/dev_20240627"
WORK = Path("models/_canary")


def _tiny_data(n=40, valid_fraction=0.25):
    return prepare_finetune_data("spider", SPIDER, BIRD, out_dir=WORK / "data",
                                 max_examples=n, valid_fraction=valid_fraction)


def canary_seq2seq():
    from text2sql.finetune.seq2seq_trainer import Seq2SeqTrainer
    from text2sql.models.hf_seq2seq_runner import HFSeq2SeqRunner
    train, valid = _tiny_data()
    out = WORK / "codet5p-spider-lora"
    adapter = Seq2SeqTrainer("Salesforce/codet5p-770m",
                             tokenizer_repo="models/codet5p-770m-tok",
                             epochs=1, batch_size=2).train(train, valid, out)
    assert Path(adapter, "adapter_config.json").exists(), "no PEFT adapter saved"
    r = HFSeq2SeqRunner("Salesforce/codet5p-770m", adapter_path=str(adapter),
                        tokenizer_repo="models/codet5p-770m-tok")
    txt = r.generate("Tables:\nstudents(id, name)\nQuestion: how many students?\nSQL:", max_tokens=24)
    print(f"SEQ2SEQ CANARY OK — adapter reloads, sample gen: {txt[:80]!r}")


def canary_mlx():
    from text2sql.finetune.mlx_trainer import MLXTrainer
    from text2sql.models.mlx_runner import MLXRunner
    train, valid = _tiny_data()
    out = WORK / "qwen-spider-lora"
    # iters=4, batch=1: just enough to prove the mlx_lm.lora subprocess runs under the
    # venv python (sys.executable fix) and writes a loadable adapter. Not for quality.
    adapter = MLXTrainer("mlx-community/Qwen3-Coder-30B-A3B-Instruct-4bit",
                         iters=4, batch_size=1).train(train, valid, out)
    assert any(Path(adapter).glob("*.safetensors")), "no mlx adapter weights saved"
    r = MLXRunner("mlx-community/Qwen3-Coder-30B-A3B-Instruct-4bit", adapter_path=str(adapter))
    txt = r.generate("Tables:\nstudents(id, name)\nQuestion: how many students?\nSQL:", max_tokens=24)
    print(f"MLX CANARY OK — adapter reloads, sample gen: {txt[:80]!r}")


def canary_codestral_text():
    # Codestral's tokenizer has no chat_template -> validate the text_format path.
    from text2sql.finetune.mlx_trainer import MLXTrainer
    from text2sql.models.mlx_runner import MLXRunner
    train, valid = _tiny_data()
    out = WORK / "codestral-spider-lora"
    adapter = MLXTrainer("mlx-community/Codestral-22B-v0.1-4bit",
                         iters=4, batch_size=1, text_format=True).train(train, valid, out)
    assert any(Path(adapter).glob("*.safetensors")), "no mlx adapter weights saved"
    r = MLXRunner("mlx-community/Codestral-22B-v0.1-4bit", adapter_path=str(adapter))
    txt = r.generate("Tables:\nstudents(id, name)\nQuestion: how many students?\nSQL:", max_tokens=24)
    print(f"CODESTRAL TEXT CANARY OK — adapter reloads, sample gen: {txt[:80]!r}")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "seq2seq"
    {"seq2seq": canary_seq2seq, "mlx": canary_mlx,
     "codestral": canary_codestral_text}[which]()
