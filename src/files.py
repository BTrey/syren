"""Discover and filter files in a directory."""

from __future__ import annotations

import fnmatch
from pathlib import Path

from .fuzzy import filter_items


def is_hidden_relative_path(relative_path: str) -> bool:
    """Return True when any path segment is a hidden name."""
    return any(segment.startswith(".") for segment in relative_path.split("/"))


def list_candidate_files(
    directory: Path,
    *,
    include_subdirs: bool,
    include_hidden: bool = False,
) -> list[str]:
    """Return relative file paths under directory."""
    directory = directory.resolve()
    paths: list[str] = []

    if include_subdirs:
        for path in sorted(directory.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(directory).as_posix()
            if not include_hidden and is_hidden_relative_path(relative):
                continue
            paths.append(relative)
    else:
        for path in sorted(directory.iterdir()):
            if not path.is_file():
                continue
            if not include_hidden and path.name.startswith("."):
                continue
            paths.append(path.name)

    return paths


def filter_filenames(
    filenames: list[str],
    pattern: str,
) -> list[str]:
    """Filter filenames by glob pattern or fuzzy subsequence match."""
    stripped = pattern.strip()
    if not stripped:
        return list(filenames)

    if any(ch in stripped for ch in "*?[]"):
        return [name for name in filenames if fnmatch.fnmatch(name, stripped)]

    scored = filter_items(stripped, filenames)
    return [name for _, name in scored]
