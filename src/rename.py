"""Validate and execute batch file renames."""

from __future__ import annotations

import uuid
from pathlib import Path


def validate_rename_plan(pairs: list[tuple[str, str]], directory: Path) -> str | None:
    """Return an error message when the rename plan is invalid."""
    directory = directory.resolve()
    active_pairs = [(source, target) for source, target in pairs if source != target]
    if not active_pairs:
        return None

    targets = [target for _, target in active_pairs]
    seen_targets: set[str] = set()
    for target in targets:
        if target in seen_targets:
            return f"Duplicate target name: {target}"
        seen_targets.add(target)

    sources = {source for source, _ in active_pairs}
    for _, target in active_pairs:
        target_path = directory / target
        if target_path.exists() and target not in sources:
            return f"Target already exists: {target}"

    return None


def execute_rename_plan(pairs: list[tuple[str, str]], directory: Path) -> None:
    """Rename files on disk using a two-phase plan to avoid collisions."""
    directory = directory.resolve()
    active_pairs = [(source, target) for source, target in pairs if source != target]
    if not active_pairs:
        return

    error = validate_rename_plan(active_pairs, directory)
    if error is not None:
        raise ValueError(error)

    temp_pairs: list[tuple[Path, Path]] = []
    final_pairs: list[tuple[Path, Path]] = []
    for source, target in active_pairs:
        source_path = directory / source
        if not source_path.is_file():
            raise ValueError(f"Source file not found: {source}")
        temp_name = f".syren-tmp-{uuid.uuid4().hex}"
        temp_path = directory / temp_name
        temp_pairs.append((source_path, temp_path))
        final_pairs.append((temp_path, directory / target))

    for source_path, temp_path in temp_pairs:
        source_path.rename(temp_path)

    try:
        for temp_path, target_path in final_pairs:
            temp_path.rename(target_path)
    except OSError as exc:
        raise ValueError(str(exc)) from exc
