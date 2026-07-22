"""Discover and filter files in a directory."""

from __future__ import annotations

import fnmatch
from pathlib import Path

from renfield.fuzzy import filter_items


def list_candidate_files(
    directory: Path,
    *,
    include_subdirs: bool,
) -> list[str]:
    """Return relative file paths under directory."""
    directory = directory.resolve()
    paths: list[str] = []

    if include_subdirs:
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                paths.append(path.relative_to(directory).as_posix())
    else:
        for path in sorted(directory.iterdir()):
            if path.is_file():
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
