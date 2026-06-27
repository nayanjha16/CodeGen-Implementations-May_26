import pytest
from text2sql.finetune import make_trainer

def test_routes_mlx():
    from text2sql.finetune.mlx_trainer import MLXTrainer
    t = make_trainer({"backend": "mlx", "mlx_repo": "x"})
    assert isinstance(t, MLXTrainer)

def test_routes_hf():
    from text2sql.finetune.hf_trainer import HFTrainer
    t = make_trainer({"backend": "hf", "hf_repo": "x"})
    assert isinstance(t, HFTrainer)

def test_routes_hf_seq2seq_with_tokenizer_repo():
    from text2sql.finetune.seq2seq_trainer import Seq2SeqTrainer
    t = make_trainer({"backend": "hf-seq2seq", "hf_repo": "x",
                      "tokenizer_repo": "models/codet5p-770m-tok"})
    assert isinstance(t, Seq2SeqTrainer)
    assert t.tokenizer_repo == "models/codet5p-770m-tok"

def test_unknown_backend_raises():
    with pytest.raises(ValueError):
        make_trainer({"backend": "nope"})
