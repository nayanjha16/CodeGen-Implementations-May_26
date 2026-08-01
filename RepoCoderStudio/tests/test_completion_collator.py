from src.completion_collator import last_subsequence_end


def test_last_subsequence_end_uses_last_match():
    assert last_subsequence_end([1, 2, 3, 1, 2, 3, 4], [1, 2, 3]) == 6


def test_last_subsequence_end_handles_absent_or_empty_pattern():
    assert last_subsequence_end([1, 2], [3]) is None
    assert last_subsequence_end([1, 2], []) is None
