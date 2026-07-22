"""Tests for fuzzy filename filtering."""

from __future__ import annotations

from renfield.fuzzy import filter_items, score_match


def test_score_match_empty_query() -> None:
    assert score_match("", "anything") == 0


def test_score_match_requires_subsequence() -> None:
    assert score_match("abc", "aXbXc") is not None
    assert score_match("abc", "acb") is None


def test_score_match_prefers_prefix_and_word_boundaries() -> None:
    prefix_score = score_match("a", "alpha")
    middle_score = score_match("a", "beta")
    assert prefix_score is not None
    assert middle_score is not None
    assert prefix_score > middle_score


def test_filter_items_returns_all_items_for_empty_query() -> None:
    items = ["b.txt", "a.txt"]
    assert filter_items("", items) == [(0, "b.txt"), (0, "a.txt")]


def test_filter_items_sorts_by_score_then_name() -> None:
    items = ["zzz.txt", "alpha.txt", "beta.txt"]
    result = filter_items("a", items)
    assert [name for _, name in result] == ["alpha.txt", "beta.txt"]
