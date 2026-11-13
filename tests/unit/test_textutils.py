"""Tests for evidence-snippet word-boundary snapping."""

from career_coach.domain.textutils import snap_slice


def test_snap_slice_starts_on_a_word_boundary():
    text = "Experience with Apache Spark and PySpark"
    result = snap_slice(text, 4, 30)
    start = text.index(result)
    assert start == 0 or text[start - 1].isspace()


def test_snap_slice_ends_on_a_word_boundary():
    text = "Experience with Apache Spark and PySpark"
    result = snap_slice(text, 4, 30)
    end = text.index(result) + len(result)
    assert end == len(text) or text[end].isspace()


def test_snap_slice_returns_full_text_when_uncropped():
    text = "alpha beta gamma"
    assert snap_slice(text, 0, len(text)) == text


def test_snap_slice_handles_text_without_spaces():
    assert snap_slice("abcdefghij", 3, 7) == "defg"
