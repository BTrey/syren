"""Tests for the transform pipeline engine."""

from __future__ import annotations

from syren.engine import INVALID_PREVIEW, apply_transforms
from syren.transforms.case import CaseTransform
from syren.transforms.prepend import PrependTransform
from syren.transforms.sub_regex import SubRegexTransform


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


def test_invalid_transform_shows_invalid_for_every_file() -> None:
    transforms = [SubRegexTransform(pattern="(a)", replacement="\\")]
    result = apply_transforms(["abc.txt", "def.txt"], transforms)
    assert result == [INVALID_PREVIEW, INVALID_PREVIEW]


def test_invalid_transform_short_circuits_rest_of_chain() -> None:
    # If the chain kept running, CaseTransform(UPPER) would turn the
    # sentinel into "INVALID". Short-circuiting keeps it unmodified.
    transforms = [
        SubRegexTransform(pattern="(a)", replacement="\\"),
        CaseTransform(mode="UPPER"),
    ]
    assert apply_transforms(["abc.txt"], transforms) == [INVALID_PREVIEW]
