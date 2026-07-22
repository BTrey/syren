"""Tests for file discovery and filtering."""

from __future__ import annotations

from pathlib import Path

from renfield.files import filter_filenames, list_candidate_files


def test_list_candidate_files_flat(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.log").write_text("b")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.txt").write_text("c")

    names = list_candidate_files(tmp_path, include_subdirs=False)
    assert names == ["a.txt", "b.log"]

    names_recursive = list_candidate_files(tmp_path, include_subdirs=True)
    assert names_recursive == ["a.txt", "b.log", "sub/c.txt"]


def test_filter_glob_and_fuzzy() -> None:
    files = ["alpha.txt", "beta.log", "gamma.txt"]
    assert filter_filenames(files, "*.txt") == ["alpha.txt", "gamma.txt"]
    assert filter_filenames(files, "bet") == ["beta.log"]
    assert filter_filenames(files, "") == files
