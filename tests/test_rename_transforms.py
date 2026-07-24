"""Tests for rename transform logic."""

from __future__ import annotations

from syren.engine import apply_transforms
from syren.transforms.base import expand_numbered
from syren.transforms.case import CaseTransform, apply_case
from syren.transforms.postpend import PostpendTransform
from syren.transforms.prepend import PrependTransform
from syren.transforms.replace import ReplaceTransform
from syren.transforms.sub_regex import SubRegexTransform


class TestExpandNumbered:
    def test_simple_counter(self) -> None:
        assert expand_numbered("#01", 0) == "01"
        assert expand_numbered("#01", 1) == "02"
        assert expand_numbered("#01", 9) == "10"

    def test_unpadded_counter(self) -> None:
        assert expand_numbered("#1", 0) == "1"
        assert expand_numbered("#1", 4) == "5"

    def test_embedded_counter(self) -> None:
        assert expand_numbered("img_#001_", 2) == "img_003_"

    def test_plain_text_unchanged(self) -> None:
        assert expand_numbered("prefix_", 3) == "prefix_"


class TestPrependTransform:
    def test_plain_prepend(self) -> None:
        transform = PrependTransform(text="new_")
        assert transform.apply("file.txt", 0) == "new_file.txt"

    def test_numbered_prepend(self) -> None:
        transform = PrependTransform(text="#01_")
        assert transform.apply("a.txt", 0) == "01_a.txt"
        assert transform.apply("b.txt", 1) == "02_b.txt"


class TestPostpendTransform:
    def test_numbered_postpend(self) -> None:
        transform = PostpendTransform(text="_#01")
        assert transform.apply("a.txt", 0) == "a.txt_01"
        assert transform.apply("a.txt", 2) == "a.txt_03"


class TestReplaceTransform:
    def test_replace(self) -> None:
        transform = ReplaceTransform(find="foo", replace="bar")
        assert transform.apply("foo.txt", 0) == "bar.txt"
        assert transform.apply("food.txt", 0) == "bard.txt"


class TestSubRegexTransform:
    def test_regex_replace(self) -> None:
        transform = SubRegexTransform(pattern=r"\d+", replacement="X")
        assert transform.apply("a12b.txt", 0) == "aXb.txt"

    def test_invalid_regex_is_noop(self) -> None:
        transform = SubRegexTransform(pattern="[", replacement="!")
        assert transform.apply("file.txt", 0) == "file.txt"


class TestCaseTransform:
    def test_upper_on_stem(self) -> None:
        transform = CaseTransform(mode="UPPER")
        assert transform.apply("hello.txt", 0) == "HELLO.txt"

    def test_sentence_on_stem(self) -> None:
        assert apply_case("hello", "sentence") == "Hello"
        transform = CaseTransform(mode="sentence")
        assert transform.apply("hello_world.txt", 0) == "Hello_world.txt"

    def test_title_on_stem(self) -> None:
        transform = CaseTransform(mode="title")
        assert transform.apply("hello_world-test.txt", 0) == "Hello_World-Test.txt"


class TestApplyTransforms:
    def test_pipeline_order(self) -> None:
        transforms = [
            ReplaceTransform(find="a", replace="b"),
            PrependTransform(text="pre_"),
        ]
        result = apply_transforms(["a.txt", "a2.txt"], transforms)
        assert result == ["pre_b.txt", "pre_b2.txt"]

    def test_index_passed_through_chain(self) -> None:
        transforms = [PrependTransform(text="#1-")]
        result = apply_transforms(["x", "y", "z"], transforms)
        assert result == ["1-x", "2-y", "3-z"]
