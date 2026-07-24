"""Tests for rename validation and execution."""

from __future__ import annotations

from pathlib import Path

import pytest

from syren.rename import execute_rename_plan, validate_rename_plan


def test_validate_allows_no_op_pairs(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a")
    assert validate_rename_plan([("a.txt", "a.txt")], tmp_path) is None


def test_validate_detects_duplicate_targets(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    error = validate_rename_plan(
        [("a.txt", "same.txt"), ("b.txt", "same.txt")],
        tmp_path,
    )
    assert error is not None
    assert "same.txt" in error


def test_validate_detects_existing_target(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    error = validate_rename_plan([("a.txt", "b.txt")], tmp_path)
    assert error is not None
    assert "b.txt" in error


def test_validate_allows_swap_when_both_in_plan(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    assert (
        validate_rename_plan([("a.txt", "b.txt"), ("b.txt", "a.txt")], tmp_path)
        is None
    )


def test_validate_allows_target_that_is_also_renamed(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    assert validate_rename_plan([("a.txt", "b.txt"), ("b.txt", "c.txt")], tmp_path) is None


def test_validate_nested_paths(tmp_path: Path) -> None:
    nested = tmp_path / "sub"
    nested.mkdir()
    (nested / "a.txt").write_text("a")
    (nested / "b.txt").write_text("b")
    error = validate_rename_plan([("sub/a.txt", "sub/b.txt")], tmp_path)
    assert error is not None


def test_execute_rename_simple(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("content")
    execute_rename_plan([("a.txt", "b.txt")], tmp_path)
    assert not (tmp_path / "a.txt").exists()
    assert (tmp_path / "b.txt").read_text() == "content"


def test_execute_rename_swap(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    execute_rename_plan([("a.txt", "b.txt"), ("b.txt", "a.txt")], tmp_path)
    assert (tmp_path / "a.txt").read_text() == "b"
    assert (tmp_path / "b.txt").read_text() == "a"


def test_execute_rename_nested(tmp_path: Path) -> None:
    nested = tmp_path / "sub"
    nested.mkdir()
    (nested / "old.txt").write_text("nested")
    execute_rename_plan([("sub/old.txt", "sub/new.txt")], tmp_path)
    assert not (nested / "old.txt").exists()
    assert (nested / "new.txt").read_text() == "nested"


def test_execute_rename_raises_on_collision(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    with pytest.raises(ValueError, match="b.txt"):
        execute_rename_plan([("a.txt", "b.txt")], tmp_path)


def test_execute_rename_ignores_no_op_pairs(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a")
    execute_rename_plan([("a.txt", "a.txt")], tmp_path)
    assert (tmp_path / "a.txt").exists()


def test_execute_rename_missing_source(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Source file not found"):
        execute_rename_plan([("missing.txt", "new.txt")], tmp_path)
