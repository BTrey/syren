"""Tests for file discovery and filtering."""

from __future__ import annotations

from pathlib import Path

from syren.files import filter_filenames, list_candidate_files


def test_list_candidate_files_flat(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.log").write_text("b")
    (tmp_path / ".hidden").write_text("secret")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.txt").write_text("c")

    names = list_candidate_files(tmp_path, include_subdirs=False)
    assert names == ["a.txt", "b.log"]

    names_with_hidden = list_candidate_files(
        tmp_path,
        include_subdirs=False,
        include_hidden=True,
    )
    assert names_with_hidden == [".hidden", "a.txt", "b.log"]

    names_recursive = list_candidate_files(tmp_path, include_subdirs=True)
    assert names_recursive == ["a.txt", "b.log", "sub/c.txt"]

    names_recursive_hidden = list_candidate_files(
        tmp_path,
        include_subdirs=True,
        include_hidden=True,
    )
    assert names_recursive_hidden == [".hidden", "a.txt", "b.log", "sub/c.txt"]


def test_list_candidate_files_skips_hidden_subpaths(tmp_path: Path) -> None:
    hidden_dir = tmp_path / ".git"
    hidden_dir.mkdir()
    (hidden_dir / "config").write_text("cfg")
    (tmp_path / "visible.txt").write_text("ok")

    names = list_candidate_files(tmp_path, include_subdirs=True, include_hidden=False)
    assert names == ["visible.txt"]

    names_with_hidden = list_candidate_files(
        tmp_path,
        include_subdirs=True,
        include_hidden=True,
    )
    assert names_with_hidden == [".git/config", "visible.txt"]


def test_is_hidden_relative_path() -> None:
    from syren.files import is_hidden_relative_path

    assert is_hidden_relative_path(".hidden")
    assert is_hidden_relative_path("sub/.secret/name")
    assert not is_hidden_relative_path("visible.txt")
    assert not is_hidden_relative_path("sub/name.txt")


def test_filter_glob_and_fuzzy() -> None:
    files = ["alpha.txt", "beta.log", "gamma.txt"]
    assert filter_filenames(files, "*.txt") == ["alpha.txt", "gamma.txt"]
    assert filter_filenames(files, "bet") == ["beta.log"]
    assert filter_filenames(files, "") == files
