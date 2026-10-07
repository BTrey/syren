"""Tests for the transform pipeline engine."""

from __future__ import annotations

from syren.engine import INVALID_PREVIEW, apply_transforms
from syren.transforms.case import CaseTransform
from syren.transforms.postpend import PostpendTransform
from syren.transforms.prepend import PrependTransform
from syren.transforms.replace import ReplaceTransform
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


def test_ignore_extension_true_transforms_whole_name() -> None:
    transforms = [PostpendTransform(text="_x")]
    result = apply_transforms(["file.txt"], transforms, ignore_extension=True)
    assert result == ["file.txt_x"]


def test_preserve_extension_is_the_default_behavior() -> None:
    # Default ignore_extension=True keeps the pre-existing behavior.
    transforms = [PostpendTransform(text="_x")]
    assert apply_transforms(["file.txt"], transforms) == ["file.txt_x"]


def test_ignore_extension_false_preserves_extension() -> None:
    transforms = [PostpendTransform(text="_x")]
    result = apply_transforms(["file.txt"], transforms, ignore_extension=False)
    assert result == ["file_x.txt"]


def test_preserve_extension_uses_last_dot() -> None:
    transforms = [PostpendTransform(text="_x")]
    result = apply_transforms(["archive.tar.gz"], transforms, ignore_extension=False)
    assert result == ["archive.tar_x.gz"]


def test_preserve_extension_on_replace_protects_suffix() -> None:
    transforms = [ReplaceTransform(find="t", replace="T")]
    result = apply_transforms(["txt.txt"], transforms, ignore_extension=False)
    assert result == ["TxT.txt"]


def test_preserve_extension_on_file_without_extension() -> None:
    transforms = [PostpendTransform(text="_x")]
    result = apply_transforms(["README"], transforms, ignore_extension=False)
    assert result == ["README_x"]


def test_preserve_extension_on_hidden_file_without_extension() -> None:
    transforms = [PrependTransform(text="new_")]
    result = apply_transforms([".gitignore"], transforms, ignore_extension=False)
    assert result == ["new_.gitignore"]


def test_preserve_extension_keeps_directory_prefix() -> None:
    transforms = [PostpendTransform(text="_x")]
    result = apply_transforms(["sub/dir/file.txt"], transforms, ignore_extension=False)
    assert result == ["sub/dir/file_x.txt"]


def test_preserve_extension_with_case_leaves_suffix() -> None:
    transforms = [CaseTransform(mode="UPPER")]
    result = apply_transforms(["photo.jpg"], transforms, ignore_extension=False)
    assert result == ["PHOTO.jpg"]


def test_invalid_transform_short_circuits_with_extension_preserved() -> None:
    transforms = [SubRegexTransform(pattern="(a)", replacement="\\")]
    result = apply_transforms(["abc.txt"], transforms, ignore_extension=False)
    assert result == [INVALID_PREVIEW]
