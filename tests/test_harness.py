import shutil

import pytest

from rustgen.eval.harness import run_rust

pytestmark = pytest.mark.skipif(
    shutil.which("rustc") is None, reason="rustc not on PATH (install via rustup)"
)

GOOD_CODE = "fn add(a: i64, b: i64) -> i64 {\n    a + b\n}"


def test_known_good_snippet_passes():
    result = run_rust(GOOD_CODE, "fn main() {\n    assert_eq!(add(2, 3), 5);\n}")
    assert result.passed
    assert result.stage == "ok"


def test_failing_assertion_is_reported():
    result = run_rust(GOOD_CODE, "fn main() {\n    assert_eq!(add(2, 2), 5);\n}")
    assert not result.passed
    assert result.stage == "run"
    assert result.stderr


def test_compile_error_is_reported():
    result = run_rust("fn broken( {", "fn main() {}")
    assert not result.passed
    assert result.stage == "compile"
    assert result.stderr
