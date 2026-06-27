def make_trainer(model_cfg: dict):
    backend = model_cfg.get("backend", "mlx")
    if backend == "mlx":
        from text2sql.finetune.mlx_trainer import MLXTrainer
        return MLXTrainer(model_cfg["mlx_repo"],
                          text_format=model_cfg.get("mlx_text_format", False))
    if backend == "hf":
        from text2sql.finetune.hf_trainer import HFTrainer
        return HFTrainer(model_cfg["hf_repo"])
    if backend == "hf-seq2seq":
        from text2sql.finetune.seq2seq_trainer import Seq2SeqTrainer
        return Seq2SeqTrainer(model_cfg["hf_repo"],
                              tokenizer_repo=model_cfg.get("tokenizer_repo"))
    raise ValueError(f"unknown backend: {backend}")
