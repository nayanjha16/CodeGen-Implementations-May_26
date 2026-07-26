"""Unit tests for text2sql hint and summary helpers."""

from __future__ import annotations

from agent.lib.text2sql_hints import (
    augment_codegen_question,
    format_deterministic_summary,
    format_listing_summary,
    question_is_open_listing,
    question_needs_aggregate_in_select,
)


def test_aggregate_question_detection() -> None:
    assert question_needs_aggregate_in_select("Which artist has the most albums?")
    assert question_needs_aggregate_in_select("How many customers are there?")
    assert not question_needs_aggregate_in_select("List album titles with artist names.")


def test_augment_codegen_question_includes_aggregate_hint() -> None:
    text = augment_codegen_question(
        "Which artist has the most albums?",
        {"Artist", "Album"},
    )
    assert "COUNT" in text
    assert '"Artist"' in text
    assert "Join them" in text


def test_deterministic_summary_when_count_missing() -> None:
    summary = format_deterministic_summary(
        question="Which artist has the most albums?",
        rows=[{"Name": "Iron Maiden"}],
    )
    assert summary is not None
    assert "Iron Maiden" in summary
    assert "top-ranked" in summary


def test_deterministic_summary_skips_when_numeric_present() -> None:
    summary = format_deterministic_summary(
        question="Which artist has the most albums?",
        rows=[{"Name": "Iron Maiden", "album_count": 21}],
    )
    assert summary is None


def test_open_listing_question_detection() -> None:
    assert question_is_open_listing("List album titles with artist names.")
    assert not question_is_open_listing("Which artist has the most albums?")


def test_augment_codegen_question_listing_hints() -> None:
    text = augment_codegen_question(
        "List album titles with artist names.",
        {"Album", "Artist"},
    )
    assert "do not add WHERE filters".lower() in text.lower()
    assert "include columns from each mentioned table".lower() in text.lower()


def test_listing_summary_when_artist_column_missing() -> None:
    summary = format_listing_summary(
        question="List album titles with artist names.",
        rows=[
            {"Title": "[1997] Black Light Syndrome"},
            {"Title": "Ace Of Spades"},
        ],
    )
    assert summary is not None
    assert "artist name" in summary.lower()
    assert "does not include" in summary.lower()
    assert "Title" in summary


def test_listing_summary_single_column_without_missing_fields() -> None:
    summary = format_listing_summary(
        question="List all artist names.",
        rows=[{"Name": "Iron Maiden"}, {"Name": "AC/DC"}],
    )
    assert summary is not None
    assert "2 row" in summary
    assert "Iron Maiden" in summary
