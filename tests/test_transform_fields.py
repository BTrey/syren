"""Tests for transform field handling edge cases."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from syren.app import RenameApp, TransformPanel
from syren.transforms.base import Transform, split_stem
from syren.transforms.case import CaseTransform, apply_case
from syren.transforms.postpend import PostpendTransform
from syren.transforms.prepend import PrependTransform
from syren.transforms.range import RangeTransform
from syren.transforms.replace import ReplaceTransform
from syren.transforms.sub_regex import SubRegexTransform


def test_split_stem_handles_hidden_files() -> None:
    assert split_stem(".gitignore") == (".gitignore", "")


def test_split_stem_handles_no_extension() -> None:
    assert split_stem("README") == ("README", "")


def test_apply_case_modes() -> None:
    assert apply_case("hello", "UPPER") == "HELLO"
    assert apply_case("HELLO", "lower") == "hello"
    assert apply_case("", "sentence") == ""
    assert apply_case("unknown", "unknown") == "unknown"


def test_apply_title_case() -> None:
    assert apply_case("hello_world", "title") == "Hello_World"
    assert apply_case("hello-world", "title") == "Hello-World"
    assert apply_case("hello world", "title") == "Hello World"
    assert apply_case("already Mixed", "title") == "Already Mixed"


def test_case_select_option_labels() -> None:
    transform = CaseTransform()
    spec = transform.field_specs()[0]
    assert ("Sentence", "sentence") in spec.select_options
    assert ("Title Case", "title") in spec.select_options


def test_case_transform_rejects_invalid_mode() -> None:
    transform = CaseTransform.from_fields({"mode": "Title"})
    assert transform.mode == "lower"


def test_case_transform_field_access() -> None:
    transform = CaseTransform(mode="UPPER")
    assert transform.get_field("mode") == "UPPER"
    transform.set_field("mode", "lower")
    assert transform.get_field("mode") == "lower"
    with pytest.raises(KeyError):
        transform.get_field("missing")
    with pytest.raises(KeyError):
        transform.set_field("missing", "lower")


def test_replace_transform_field_access() -> None:
    transform = ReplaceTransform(find="a", replace="b")
    assert transform.get_field("find") == "a"
    assert transform.get_field("replace") == "b"
    transform.set_field("find", "x")
    transform.set_field("replace", "y")
    assert transform.find == "x"
    assert transform.replace == "y"
    with pytest.raises(KeyError):
        transform.get_field("missing")


def test_replace_transform_empty_find_is_noop() -> None:
    transform = ReplaceTransform(find="", replace="x")
    assert transform.apply("file.txt", 0) == "file.txt"


def test_prepend_transform_field_access() -> None:
    transform = PrependTransform(text="pre_")
    assert transform.get_field("text") == "pre_"
    transform.set_field("text", "new_")
    assert transform.text == "new_"
    with pytest.raises(KeyError):
        transform.set_field("missing", "x")


def test_postpend_transform_field_access() -> None:
    transform = PostpendTransform(text="_suf")
    assert transform.get_field("text") == "_suf"
    transform.set_field("text", "_end")
    assert transform.text == "_end"
    with pytest.raises(KeyError):
        transform.get_field("missing")


def test_sub_regex_transform_field_access() -> None:
    transform = SubRegexTransform(pattern=r"\d+", replacement="N")
    assert transform.get_field("pattern") == r"\d+"
    assert transform.get_field("replacement") == "N"
    transform.set_field("pattern", r"[a-z]+")
    transform.set_field("replacement", "word")
    assert transform.pattern == r"[a-z]+"
    assert transform.replacement == "word"
    with pytest.raises(KeyError):
        transform.set_field("missing", "x")


def test_sub_regex_empty_pattern_is_noop() -> None:
    transform = SubRegexTransform(pattern="", replacement="!")
    assert transform.apply("file.txt", 0) == "file.txt"


def test_transform_to_dict_round_trip_fields() -> None:
    transform = SubRegexTransform(pattern=r"\d+", replacement="N")
    data = transform.to_dict()
    assert data["type"] == "sub_regex"
    assert data["fields"]["pattern"] == r"\d+"


def test_transform_from_dict_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        Transform.from_dict({})


def test_range_transform_fields_render_on_one_row(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = RenameApp(tmp_path)
        app.transforms.append(RangeTransform(start="0", end="3"))
        async with app.run_test() as pilot:
            app.refresh_transform_panels()
            await pilot.pause()
            panel = app.query(TransformPanel).first()
            start_input = panel.query_one("#field-0-start")
            end_input = panel.query_one("#field-0-end")
            assert start_input.region.y == end_input.region.y

    asyncio.run(scenario())
