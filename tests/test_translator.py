from rustgen.config import Config
from rustgen.translator import get_translator
from rustgen.translator.base import TranslationTask
from rustgen.translator.mock import MockTranslator


def test_factory_returns_mock_by_default():
    assert isinstance(get_translator(Config()), MockTranslator)


def test_english_to_rust_returns_rust():
    task = TranslationTask(description="Add two integers and return the sum.")
    out = MockTranslator().generate(task)
    assert "fn " in out
    assert "Add two integers and return the sum." in out


def test_python_to_rust_returns_rust():
    task = TranslationTask(
        description="Add two numbers.",
        python_code="def add(a, b):\n    return a + b",
    )
    out = MockTranslator().generate(task)
    assert "fn " in out
    assert "Python -> Rust" in out


def test_mock_is_deterministic():
    task = TranslationTask(description="Reverse a string.")
    translator = MockTranslator()
    assert translator.generate(task) == translator.generate(task)


def test_trim_to_body_ignores_braces_in_strings_and_chars():
    from rustgen.translator.hf import trim_to_body

    completion = (
        '    println!("closing brace }} in a string");\n'
        "    let c = '}';\n"
        "    return 1;\n"
        "}\n"
        "fn next_function() {"
    )
    body = trim_to_body(completion)
    assert body.rstrip().endswith("return 1;")
    assert "next_function" not in body


def test_trim_to_first_fn_keeps_whole_function():
    from rustgen.translator.hf import trim_to_first_fn

    code = 'fn greet() {\n    println!("{}", "hi");\n}\nfn extra() {}'
    trimmed = trim_to_first_fn(code)
    assert trimmed.endswith("}")
    assert "extra" not in trimmed


def test_extract_python_from_fenced_block():
    from rustgen.translator.pivot import extract_python_function

    text = ("Here is the function:\n```python\nimport math\n\n"
            "def area(r):\n    return math.pi * r * r\n```\nHope this helps!")
    code = extract_python_function(text)
    assert code == "import math\ndef area(r):\n    return math.pi * r * r"


def test_extract_python_from_raw_code_keeps_first_fn_only():
    from rustgen.translator.pivot import extract_python_function

    text = "def add(a, b):\n    return a + b\n\ndef extra():\n    pass"
    code = extract_python_function(text)
    assert "def add" in code and "extra" not in code


def test_extract_python_rejects_garbage():
    from rustgen.translator.pivot import extract_python_function

    assert extract_python_function("Sorry, I can't do that.") is None
    assert extract_python_function("x = 1\ny = 2") is None  # no function
    assert extract_python_function("def broken(:\n    pass") is None  # syntax error


def test_extract_rust_main_keeps_only_main():
    from rustgen.translator.pivot import extract_rust_main

    text = ("```rust\n"
            "fn add(a: i64, b: i64) -> i64 { a + b }\n\n"   # smuggled solution
            "fn main() {\n    assert_eq!(add(1, 2), 3);\n    assert_eq!(add(0, 0), 0);\n}\n"
            "```")
    tests = extract_rust_main(text)
    assert tests.startswith("fn main()")
    assert "assert_eq!(add(1, 2), 3)" in tests
    assert "fn add" not in tests  # the smuggled implementation is dropped


def test_extract_rust_main_rejects_output_without_asserts():
    from rustgen.translator.pivot import extract_rust_main

    assert extract_rust_main("fn main() { println!(\"hi\"); }") is None
    assert extract_rust_main("no code here") is None


def test_extract_rust_signature_strips_body_and_fences():
    from rustgen.translator.pivot import extract_rust_signature

    text = "```rust\nfn count_even(nums: Vec<isize>) -> isize {\n    0\n}\n```"
    assert extract_rust_signature(text) == "fn count_even(nums: Vec<isize>) -> isize"
    assert extract_rust_signature("fn add(a: i64, b: i64) -> i64;") == \
        "fn add(a: i64, b: i64) -> i64"
    assert extract_rust_signature("no signature here") is None
