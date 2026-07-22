"""Tests for the transform pipeline engine."""

from __future__ import annotations

from renfield.engine import apply_transforms
from renfield.transforms.prepend import PrependTransform


def test_apply_transforms_with_no_transforms_returns_copy() -> None:
    filenames = ["a.txt", "b.txt"]
    assert apply_transforms(filenames, []) == filenames


def test_apply_transforms_with_empty_input() -> None:
    transforms = [PrependTransform(text="x")]
    assert apply_transforms([], transforms) == []
