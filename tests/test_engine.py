"""Tests for the transform pipeline engine."""

from __future__ import annotations

from syren.engine import apply_transforms
from syren.transforms.prepend import PrependTransform


def test_apply_transforms_with_no_transforms_returns_copy() -> None:
    filenames = ["a.txt", "b.txt"]
    assert apply_transforms(filenames, []) == filenames


def test_apply_transforms_with_empty_input() -> None:
    transforms = [PrependTransform(text="x")]
    assert apply_transforms([], transforms) == []


def test_apply_transforms_only_changes_basename_in_subdirs() -> None:
    transforms = [PrependTransform(text="new_")]
    result = apply_transforms(["sub/dir/file.txt"], transforms)
    assert result == ["sub/dir/new_file.txt"]


def test_apply_transforms_preserves_directory_names_in_pipeline() -> None:
    transforms = [
        PrependTransform(text="x_"),
        PrependTransform(text="y_"),
    ]
    result = apply_transforms(["folder/name.txt"], transforms)
    assert result == ["folder/y_x_name.txt"]
