"""Apply an ordered list of transforms to filenames."""

from __future__ import annotations

from .transforms.base import Transform


def apply_transforms(
    filenames: list[str],
    transforms: list[Transform],
) -> list[str]:
    """Apply each transform to each filename, in list order."""
    results: list[str] = []
    for file_index, filename in enumerate(filenames):
        current = filename
        for transform in transforms:
            current = transform.apply(current, file_index)
        results.append(current)
    return results
