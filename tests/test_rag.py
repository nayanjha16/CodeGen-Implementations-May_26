import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from rustgen.config import Config
from rustgen.rag import get_retriever
from rustgen.rag.idioms import IDIOM_EXEMPLARS
from rustgen.rag.prompt import build_prompt, retrieval_query
from rustgen.rag.retriever import MockRetriever
from rustgen.translator.base import TranslationTask


def test_mock_retriever_returns_k_snippets():
    retriever = MockRetriever()
    for k in (1, 3, 5):
        examples = retriever.retrieve("sum a list of numbers", k)
        assert len(examples) == k
        assert all("fn " in example for example in examples)


def test_get_retriever_default_is_mock():
    assert isinstance(get_retriever(Config()), MockRetriever)


def test_tfidf_retriever_ranks_by_similarity(tmp_path):
    pytest.importorskip("sklearn")
    from rustgen.rag.retriever import TfidfRetriever

    docs = [
        "fn add(a: i64, b: i64) -> i64 { a + b }",
        "fn reverse_string(s: &str) -> String { s.chars().rev().collect() }",
        "fn is_prime(n: u64) -> bool { n > 1 && (2..=n / 2).all(|d| n % d != 0) }",
    ]
    corpus = tmp_path / "corpus.jsonl"
    corpus.write_text("\n".join(json.dumps({"content": doc}) for doc in docs))

    retriever = TfidfRetriever(str(corpus))
    results = retriever.retrieve("add two numbers", 2)
    assert len(results) == 2
    assert results[0] == docs[0]


def test_build_prompt_matches_trained_format():
    # The Step 3b fine-tune trained on: Python-as-comment FIRST, then the
    # `///` description, then the signature ending in ` {`. Any drift here
    # makes the real model see out-of-distribution prompts.
    task = TranslationTask(
        description="Add two integers.",
        python_code="def add(a, b):\n    return a + b",
        signature="fn add(a: i64, b: i64) -> i64",
    )
    prompt = build_prompt(task, [])
    assert prompt == (
        "// Reference Python implementation:\n"
        "// def add(a, b):\n"
        "//     return a + b\n"
        "/// Add two integers.\n"
        "fn add(a: i64, b: i64) -> i64 {\n"
    )


def test_build_prompt_examples_precede_task():
    task = TranslationTask(description="Add two integers.",
                           signature="fn add(a: i64, b: i64) -> i64 {")
    prompt = build_prompt(task, ["fn one() -> i64 {\n    1\n}"])
    assert prompt.startswith("fn one() -> i64 {")
    assert prompt.index("fn one()") < prompt.index("/// Add two integers.")
    # a signature already ending in `{` is not double-braced
    assert prompt.endswith("fn add(a: i64, b: i64) -> i64 {\n")


def test_build_prompt_without_examples_or_extras():
    prompt = build_prompt(TranslationTask(description="Reverse a string."), [])
    assert prompt == "/// Reverse a string.\n"


_PAIRS = [
    {"task": "t1", "python": "def one():\n    return 1",
     "rust_prompt": "/// One.\nfn one() -> i64 {\n",
     "rust_solution": "/// One.\nfn one() -> i64 {\n    1\n}"},
    {"task": "t1", "python": "def one():\n    return 1",
     "rust_prompt": "/// One.\nfn one() -> i64 {\n",
     "rust_solution": "/// One.\nfn one() -> i64 {\n    let x = 1;\n    x\n}"},
]


def test_build_corpus_emits_trained_blocks(tmp_path):
    from rustgen.rag.build_corpus import build_corpus

    src = tmp_path / "pairs.jsonl"
    src.write_text("\n".join(json.dumps(p) for p in _PAIRS))
    out = tmp_path / "corpus.jsonl"

    n = build_corpus(src, out, style="translation")
    assert n == 1  # duplicate task collapsed to the shortest solution
    doc = json.loads(out.read_text())
    assert doc["content"].startswith("// Reference Python implementation:\n// def one():")
    assert doc["content"].endswith("fn one() -> i64 {\n    1\n}")


def test_build_corpus_completion_style_is_pure_rust(tmp_path):
    # The Qwen/Step 6 format: content = the bare Rust function, plus a
    # retrieval_text of doc comment + signature for the index side.
    from rustgen.rag.build_corpus import build_corpus

    src = tmp_path / "pairs.jsonl"
    src.write_text("\n".join(json.dumps(p) for p in _PAIRS))
    out = tmp_path / "corpus.jsonl"

    n = build_corpus(src, out, style="completion")
    assert n == 1
    doc = json.loads(out.read_text())
    assert doc["content"] == "/// One.\nfn one() -> i64 {\n    1\n}"
    assert doc["retrieval_text"] == "/// One.\nfn one() -> i64 {\n"
    assert "// def one" not in doc["content"]


def test_retrieval_query_is_doc_comment_plus_signature():
    # Step 6 retrieved by Rust-prompt similarity: the query must carry ONLY
    # what the model has at completion time — never the Python source.
    task = TranslationTask(
        description="Add two integers.",
        python_code="def add(a, b):\n    return a + b",
        signature="fn add(a: i64, b: i64) -> i64",
    )
    query = retrieval_query(task)
    assert query == "/// Add two integers.\nfn add(a: i64, b: i64) -> i64 {\n"
    assert "def add" not in query
    assert retrieval_query(TranslationTask(description="Reverse.")) == "/// Reverse.\n"


def test_tfidf_retriever_indexes_retrieval_text_but_returns_content(tmp_path):
    pytest.importorskip("sklearn")
    from rustgen.rag.retriever import TfidfRetriever

    docs = [
        {"content": "fn multiply(a: i64, b: i64) -> i64 { a * b }",
         "retrieval_text": "/// Multiply two numbers.\nfn multiply(a: i64, b: i64) -> i64 {\n"},
        {"content": "fn shout(s: &str) -> String { s.to_uppercase() }",
         "retrieval_text": "/// Uppercase a string.\nfn shout(s: &str) -> String {\n"},
    ]
    corpus = tmp_path / "corpus.jsonl"
    corpus.write_text("\n".join(json.dumps(d) for d in docs))

    retriever = TfidfRetriever(str(corpus))
    results = retriever.retrieve("/// Multiply two numbers together.\nfn product(x: i64, y: i64) -> i64 {\n", 1)
    assert results == [docs[0]["content"]]


def test_idiom_exemplars_are_ten_wellformed_functions():
    assert len(IDIOM_EXEMPLARS) == 10
    assert len({e["task"] for e in IDIOM_EXEMPLARS}) == 10
    for e in IDIOM_EXEMPLARS:
        assert e["rust_solution"].startswith("///")
        assert e["rust_solution"].rstrip().endswith("}")
        assert e["rust_prompt"].startswith("///")
        assert not e["rust_prompt"].endswith("{")  # bare signature on the index side
        assert "fn " in e["rust_prompt"]


@pytest.mark.skipif(shutil.which("rustc") is None, reason="rustc not installed")
def test_idiom_exemplars_compile():
    # The exemplars teach compile-error fixes — they must themselves compile.
    for e in IDIOM_EXEMPLARS:
        with tempfile.TemporaryDirectory() as wd:
            src = Path(wd) / "lib.rs"
            src.write_text(e["rust_solution"] + "\n")
            result = subprocess.run(
                ["rustc", "--crate-type", "lib", str(src), "--out-dir", wd],
                capture_output=True, text=True)
            assert result.returncode == 0, f"{e['task']}:\n{result.stderr}"


def test_nearest_idiom_matches_topic():
    pytest.importorskip("sklearn")
    from rustgen.rag.idioms import nearest_idiom

    floats = nearest_idiom("/// Return the largest element of a list of floats.\n"
                           "fn max_elem(values: Vec<f64>) -> f64 {\n")
    assert "f64" in floats
    strings = nearest_idiom("/// Return the character of a string at a position.\n"
                            "fn pick(s: String, k: usize) -> char {\n")
    assert "chars()" in strings
