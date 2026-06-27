from pathlib import Path
from text2sql.finetune.orchestrator import prepare_finetune_data

FIX = Path(__file__).parents[1] / "data" / "fixtures"

def test_prepare_writes_train_and_valid(tmp_path):
    train, valid = prepare_finetune_data(
        dataset="spider", spider_root=FIX / "spider_mini", bird_root=FIX / "bird_mini",
        out_dir=tmp_path, valid_fraction=0.0)
    assert Path(train).exists()
    assert Path(valid).exists()


def test_combined_includes_both_datasets(tmp_path):
    # holdout=0 so the tiny 1-example bird fixture isn't dropped. The interleave puts
    # bird right after spider, so both datasets are represented across train+valid.
    # (The real all-spider-before-bird bug needs spider_count > cap; spot-checked on
    # real data during the run — fixtures have 1 example each.)
    train, valid = prepare_finetune_data(
        dataset="combined", spider_root=FIX / "spider_mini", bird_root=FIX / "bird_mini",
        out_dir=tmp_path, valid_fraction=0.0, bird_eval_holdout=0)
    text = (Path(train).read_text() + Path(valid).read_text()).lower()
    assert "singer" in text   # spider example present (concert_singer db)
    assert "school" in text   # bird example present (california_schools db)
