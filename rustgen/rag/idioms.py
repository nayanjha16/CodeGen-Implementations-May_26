"""The ten idiom exemplars from the Step 5 error analysis.

The vanilla-Qwen compile errors concentrate in a few Python-habit idioms:
indexing with `isize`, ordering floats, int/float mixing, helper functions
never defined, values moved instead of borrowed. Each exemplar below
demonstrates the Rust-side fix for one bucket.

Step 6 measured how to use them: merged into the open RAG index they are
almost never retrieved (top-2 for only 4 of 34 compile-error problems), so
the cascade's fallback attempt ALWAYS prepends the single nearest idiom on
top of the k=2 retrieved examples. That fallback recovered 9 of the 11
compile errors the 44.9% cascade fixed.

All ten are rustc-verified (see tests/test_rag.py).
"""

from __future__ import annotations

_SOLUTIONS = {
    "idiom_index_with_cast": """\
/// Return the element at position i of a list, where i is given as an isize.
fn element_at(values: Vec<isize>, i: isize) -> isize {
    values[i as usize]
}""",
    "idiom_max_of_floats": """\
/// Return the largest value in a non-empty list of floats.
fn max_float(values: Vec<f64>) -> f64 {
    values.iter().cloned().fold(f64::NEG_INFINITY, f64::max)
}""",
    "idiom_sort_floats": """\
/// Return a copy of the list of floats sorted in increasing order.
fn sort_floats(values: Vec<f64>) -> Vec<f64> {
    let mut sorted = values.clone();
    sorted.sort_by(|a, b| a.partial_cmp(b).unwrap());
    sorted
}""",
    "idiom_nested_helper_fn": """\
/// Return true if the sum of the digits of n is a prime number.
fn digit_sum_is_prime(n: isize) -> bool {
    fn is_prime(x: isize) -> bool {
        if x < 2 {
            return false;
        }
        for d in 2..=((x as f64).sqrt() as isize) {
            if x % d == 0 {
                return false;
            }
        }
        true
    }
    let mut s = 0;
    let mut m = n.abs();
    while m > 0 {
        s += m % 10;
        m /= 10;
    }
    is_prime(s)
}""",
    "idiom_int_float_mix": """\
/// Return the average of a non-empty list of integers as a float.
fn average(values: Vec<isize>) -> f64 {
    let total: isize = values.iter().sum();
    total as f64 / values.len() as f64
}""",
    "idiom_widen_to_avoid_overflow": """\
/// Return the product of all elements, computed in i64 so it cannot overflow i32.
fn product_wide(values: Vec<i32>) -> i64 {
    values.iter().map(|&v| v as i64).product()
}""",
    "idiom_string_compare": """\
/// Return true if two words are equal ignoring case.
fn same_word(a: String, b: String) -> bool {
    a.to_lowercase() == b.to_lowercase()
}""",
    "idiom_char_at_position": """\
/// Return the character at position k of a string (character, not byte, index).
fn char_at(s: String, k: usize) -> char {
    s.chars().nth(k).unwrap_or(' ')
}""",
    "idiom_iterate_by_reference": """\
/// Return the difference between the largest and smallest element,
/// iterating by reference so the vector is not moved.
fn value_range(values: Vec<isize>) -> isize {
    let max = values.iter().max().unwrap();
    let min = values.iter().min().unwrap();
    max - min
}""",
    "idiom_enumerate_positions": """\
/// Return the positions at which a negative number appears in the list.
fn negative_positions(values: Vec<isize>) -> Vec<usize> {
    values.iter().enumerate()
          .filter(|&(_, &v)| v < 0)
          .map(|(i, _)| i)
          .collect()
}""",
}


def _doc_and_signature(solution: str) -> str:
    """The retrievable face of an exemplar: `///` doc lines + bare signature —
    the same document shape the Step 6 index used."""
    lines = solution.splitlines()
    doc = [line for line in lines if line.startswith("///")]
    signature = next(line for line in lines if line.startswith("fn "))
    return "\n".join(doc + [signature.rstrip(" {")])


IDIOM_EXEMPLARS: list[dict[str, str]] = [
    {"task": task, "rust_prompt": _doc_and_signature(sol), "rust_solution": sol}
    for task, sol in _SOLUTIONS.items()
]

_index = None


def nearest_idiom(query: str) -> str:
    """The single most similar idiom exemplar (whole function) for this query.

    Same TF-IDF settings as the retriever, but over the ten idioms only —
    guaranteed inclusion, not open retrieval (see module docstring).
    """
    global _index
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError as exc:
        raise ImportError(
            "nearest_idiom needs scikit-learn: pip install -e '.[rag]'"
        ) from exc
    if _index is None:
        vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
        matrix = vectorizer.fit_transform([e["rust_prompt"] for e in IDIOM_EXEMPLARS])
        _index = (vectorizer, matrix)
    vectorizer, matrix = _index
    sims = cosine_similarity(vectorizer.transform([query]), matrix)[0]
    return IDIOM_EXEMPLARS[int(sims.argmax())]["rust_solution"]
