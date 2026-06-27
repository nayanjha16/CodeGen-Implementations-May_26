from itertools import zip_longest
from pathlib import Path
from text2sql.data.spider import SpiderDataset
from text2sql.data.bird import BirdDataset
from text2sql.finetune.dataset import build_finetune_jsonl

def _load(dataset, spider_root, bird_root):
    if dataset == "spider":
        return SpiderDataset(root=spider_root, split="train")
    if dataset == "bird":
        return BirdDataset(root=bird_root, split="train")
    raise ValueError(dataset)

def prepare_finetune_data(dataset, spider_root, bird_root, out_dir, valid_fraction=0.05,
                          max_examples=None, bird_eval_holdout=200):
    """Build train/valid jsonl for fine-tuning.

    BIRD has no local train split, so finetuned_bird would otherwise train on the
    same dev examples it is later evaluated on. To keep train/eval DISJOINT (and
    eval still comparable to the zero/one-shot cells, which score the first
    `sample_size`=200 dev examples), we hold out the first `bird_eval_holdout` dev
    examples and train BIRD only on the remainder (the tail). Spider is unaffected
    — it has a real train split separate from dev.
    """
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    def _bird_train():
        # drop the eval window (dev[:holdout]); train on dev[holdout:]
        return _load("bird", spider_root, bird_root).examples()[bird_eval_holdout:]

    if dataset == "combined":
        # Interleave spider/bird so a `max_examples` cap draws ~50/50 from BOTH
        # datasets. (Plain concatenation + [:1000] would yield all-spider/no-bird.)
        spider_ex = _load("spider", spider_root, bird_root).examples()
        bird_ex = _bird_train()
        examples = [x for pair in zip_longest(spider_ex, bird_ex) for x in pair if x is not None]
        ds_for_schema = {"spider": _load("spider", spider_root, bird_root),
                         "bird": _load("bird", spider_root, bird_root)}
    elif dataset == "bird":
        examples = _bird_train()
        ds_for_schema = {"bird": _load("bird", spider_root, bird_root)}
    else:
        ds = _load(dataset, spider_root, bird_root)
        examples = ds.examples()
        ds_for_schema = {dataset: ds}

    if max_examples:                      # sample-first fine-tuning
        examples = examples[:max_examples]

    def schema_for(db_id):
        for ds in ds_for_schema.values():
            try:
                return ds.schema(db_id), ds.db_path(db_id)
            except KeyError:
                continue
        raise KeyError(db_id)

    schemas, db_paths = {}, {}
    for ex in examples:
        if ex.db_id not in schemas:
            s, p = schema_for(ex.db_id)
            schemas[ex.db_id], db_paths[ex.db_id] = s, p

    n_valid = max(1, int(len(examples) * valid_fraction)) if len(examples) > 1 else 1
    valid_ex = examples[:n_valid]
    train_ex = examples[n_valid:] or examples

    train_path = out_dir / "train.jsonl"
    valid_path = out_dir / "valid.jsonl"
    build_finetune_jsonl(train_ex, schemas, db_paths, train_path)
    build_finetune_jsonl(valid_ex, schemas, db_paths, valid_path)
    return train_path, valid_path
