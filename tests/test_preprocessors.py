from __future__ import annotations

import json
from pathlib import Path

from codegen_rag.data.preprocessors import (
    CodeDocRecord,
    clean_code_text,
    clean_rust_corpus,
    deduplicate,
    extract_function_name,
    mix_anti_forgetting_samples,
    parse_codocbench_directory,
    strip_docstring,
    train_val_test_split,
)


def test_clean_code_text_rejects_too_short():
    assert clean_code_text("x=1", min_len=20, max_len=8000) is None


def test_clean_code_text_normalizes_whitespace():
    raw = "def f():\r\n\tpass\r\n"
    cleaned = clean_code_text(raw, min_len=1, max_len=8000)
    assert "\r" not in cleaned
    assert "\t" not in cleaned


def test_strip_docstring_python():
    code = 'def f():\n    """Does a thing."""\n    return 1'
    code_wo_doc, doc = strip_docstring(code, "python")
    assert doc == "Does a thing."
    assert '"""' not in code_wo_doc


def test_extract_function_name_python():
    assert extract_function_name("def my_func(x, y):\n    return x", "python") == "my_func"


def test_extract_function_name_java():
    code = "public int myMethod(int x) {\n    return x;\n}"
    assert extract_function_name(code, "java") == "myMethod"


def test_deduplicate_drops_exact_duplicates():
    records = [
        CodeDocRecord(code="def f(): pass", docstring="a", language="python"),
        CodeDocRecord(code="def f(): pass", docstring="b", language="python"),
        CodeDocRecord(code="def g(): pass", docstring="c", language="python"),
    ]
    unique = deduplicate(records)
    assert len(unique) == 2


def test_train_val_test_split_ratios_and_disjoint():
    records = list(range(100))
    splits = train_val_test_split(records, train_ratio=0.8, val_ratio=0.1, seed=1)
    assert len(splits["train"]) == 80
    assert len(splits["val"]) == 10
    assert len(splits["test"]) == 10
    all_ids = splits["train"] + splits["val"] + splits["test"]
    assert sorted(all_ids) == list(range(100))


def test_train_val_test_split_is_deterministic():
    records = list(range(50))
    a = train_val_test_split(records, seed=7)
    b = train_val_test_split(records, seed=7)
    assert a["train"] == b["train"]


def test_clean_rust_corpus_dedupes_and_filters():
    samples = [
        {"code": "fn main() { println!(\"hi\"); }", "language": "rust"},
        {"code": "fn main() { println!(\"hi\"); }", "language": "rust"},  # duplicate
        {"code": "x", "language": "rust"},  # too short
    ]
    cleaned = clean_rust_corpus(samples, min_len=5, max_len=8000)
    assert len(cleaned) == 1


def test_mix_anti_forgetting_samples_ratio():
    target = [{"code": f"fn f{i}() {{}}"} for i in range(85)]
    source = [{"code": f"def f{i}(): pass"} for i in range(1000)]
    mixed = mix_anti_forgetting_samples(target, source, anti_forgetting_ratio=0.15, seed=3)
    # ~15% of the combined set should be source-language samples
    n_source_in_mix = sum(1 for m in mixed if m["code"].startswith("def"))
    ratio = n_source_in_mix / len(mixed)
    assert 0.10 < ratio < 0.20


def test_parse_codocbench_directory_handles_json_list(tmp_path: Path):
    lang_dir = tmp_path / "data" / "python"
    lang_dir.mkdir(parents=True)
    payload = [
        {
            "code": "def add(a, b):\n    return a + b",
            "docstring": "Adds two numbers.",
            "diff": "- pass\n+ return a + b",
            "commit_message": "implement add",
        }
    ]
    (lang_dir / "sample.json").write_text(json.dumps(payload), encoding="utf-8")

    records = parse_codocbench_directory(tmp_path, languages=["python"], min_len=1)
    assert len(records) == 1
    assert records[0].function_name == "add"
    assert records[0].commit_message == "implement add"


def test_parse_codocbench_directory_skips_malformed_file(tmp_path: Path, caplog):
    lang_dir = tmp_path / "data" / "python"
    lang_dir.mkdir(parents=True)
    (lang_dir / "broken.json").write_text("{not valid json", encoding="utf-8")

    records = parse_codocbench_directory(tmp_path, languages=["python"], min_len=1)
    assert records == []


def test_parse_codocbench_directory_handles_real_nested_release_shape(tmp_path: Path):
    """CoDocBench's actual release format: dataset/codocbench.jsonl with
    code/docstring nested inside version_data, not flat top-level keys.
    Regression test for the bug where this real shape parsed to 0 records."""
    dataset_dir = tmp_path / "dataset"
    dataset_dir.mkdir(parents=True)
    entry = {
        "file": "mymodule.py",
        "function": "mypkg.mymodule.add_numbers",
        "version_data": [
            {
                "version1": "abc123",
                "docstring": "Adds two numbers together.",
                "code": "def add_numbers(a, b):\n    return a + b",
                "commit_message": "initial implementation",
            },
            {
                "version2": "def456",
                "docstring": "Adds two numbers together, returning an int.",
                "code": "def add_numbers(a: int, b: int) -> int:\n    return a + b",
                "commit_message": "add type hints",
            },
        ],
        "diff_code": "- def add_numbers(a, b):\n+ def add_numbers(a: int, b: int) -> int:",
        "file_path": "src/mymodule.py",
        "project": "example-project",
        "owner": "example-owner",
    }
    (dataset_dir / "codocbench.jsonl").write_text(json.dumps(entry) + "\n", encoding="utf-8")

    records = parse_codocbench_directory(tmp_path, languages=["python"], min_len=1)

    assert len(records) == 2
    assert all(r.function_name == "add_numbers" for r in records)
    assert all(r.source_file == "src/mymodule.py" for r in records)
    assert records[0].intent == "Adds two numbers together."
    assert records[0].docstring == records[0].intent
    assert records[0].commit_message == "initial implementation"
    assert records[1].commit_message == "add type hints"


def test_parse_codocbench_directory_java_yields_nothing_for_real_layout(tmp_path: Path):
    """CoDocBench has no Java/C++ data at all -- this documents that as
    expected behavior (not a bug) rather than something to silently paper over."""
    dataset_dir = tmp_path / "dataset"
    dataset_dir.mkdir(parents=True)
    entry = {"function": "x", "version_data": [{"code": "def f(): pass", "docstring": "d"}]}
    (dataset_dir / "codocbench.jsonl").write_text(json.dumps(entry) + "\n", encoding="utf-8")

    records = parse_codocbench_directory(tmp_path, languages=["java"], min_len=1)
    assert records == []
