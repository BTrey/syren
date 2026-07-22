"""Fzf-style subsequence fuzzy matching."""

from __future__ import annotations


def score_match(query: str, text: str) -> int | None:
    """Return a match score, or None if query is not a subsequence of text."""
    if not query:
        return 0

    q = query.lower()
    t = text.lower()
    q_len = len(q)
    t_len = len(t)

    score = 0
    q_idx = 0
    prev_match = -1
    consecutive = 0

    for i, ch in enumerate(t):
        if q_idx < q_len and ch == q[q_idx]:
            score += 1
            if prev_match == i - 1:
                consecutive += 1
                score += consecutive * 5
            else:
                consecutive = 0
                if i == 0 or not t[i - 1].isalnum():
                    score += 10
                if i > 0 and t[i - 1] in "/._-:":
                    score += 8

            prev_match = i
            q_idx += 1

    if q_idx != q_len:
        return None

    score += max(0, 200 - (t_len - q_len))
    return score


def filter_items(query: str, items: list[str]) -> list[tuple[int, str]]:
    """Filter and rank items by fuzzy match score (highest first)."""
    if not query:
        return [(0, item) for item in items]

    scored: list[tuple[int, str]] = []
    for item in items:
        match_score = score_match(query, item)
        if match_score is not None:
            scored.append((match_score, item))

    scored.sort(key=lambda pair: (-pair[0], pair[1].lower()))
    return scored
