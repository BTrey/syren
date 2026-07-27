"""Tests for the Range filename transform."""

from __future__ import annotations

import pytest

from syren.engine import apply_transforms
from syren.transforms.range import RangeTransform, apply_range


class TestApplyRange:
    def test_extracts_inclusive_range(self) -> None:
        assert apply_range("filename.txt", 2, 5) == "lena"

    def test_single_character_range(self) -> None:
        assert apply_range("abc", 1, 1) == "b"

    def test_full_string_range(self) -> None:
        assert apply_range("abc", 0, 2) == "abc"

    def test_start_greater_than_end_returns_empty(self) -> None:
        assert apply_range("abc", 2, 0) == ""

    def test_clamps_to_string_bounds(self) -> None:
        assert apply_range("abc", 0, 99) == "abc"
        assert apply_range("abc", 5, 10) == ""


class TestRangeTransform:
    def test_apply_with_valid_fields(self) -> None:
        transform = RangeTransform(start="2", end="5")
        assert transform.apply("filename.txt", 0) == "lena"

    def test_empty_fields_are_noop(self) -> None:
        transform = RangeTransform(start="", end="")
        assert transform.apply("filename.txt", 0) == "filename.txt"

    def test_invalid_fields_are_noop(self) -> None:
        transform = RangeTransform(start="x", end="5")
        assert transform.apply("filename.txt", 0) == "filename.txt"

    def test_field_specs(self) -> None:
        transform = RangeTransform()
        keys = [spec.key for spec in transform.field_specs()]
        assert keys == ["start", "end"]
        groups = [spec.group for spec in transform.field_specs()]
        assert groups == ["indices", "indices"]

    def test_field_access(self) -> None:
        transform = RangeTransform(start="1", end="3")
        assert transform.get_field("start") == "1"
        assert transform.get_field("end") == "3"
        transform.set_field("start", "0")
        transform.set_field("end", "2")
        assert transform.start == "0"
        assert transform.end == "2"
        with pytest.raises(KeyError):
            transform.get_field("missing")
        with pytest.raises(KeyError):
            transform.set_field("missing", "0")

    def test_from_fields(self) -> None:
        transform = RangeTransform.from_fields({"start": "0", "end": "1"})
        assert transform.start == "0"
        assert transform.end == "1"

    def test_in_pipeline(self) -> None:
        transforms = [RangeTransform(start="0", end="2")]
        assert apply_transforms(["hello.txt"], transforms) == ["hel"]
