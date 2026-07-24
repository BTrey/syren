"""Apply an ordered list of transforms to filenames."""

from __future__ import annotations

from .transforms.base import Transform


def apply_transforms(
    filenames: list[str],
    transforms: list[Transform],
) -> list[str]:
    """Apply each transform to each filename basename, in list order."""
    if not transforms:
        return list(filenames)

    results: list[str] = []
    for file_index, filename in enumerate(filenames):
        parent, separator, basename = filename.rpartition("/")
        current = basename
        for transform in transforms:
            current = transform.apply(current, file_index)
        if separator:
            results.append(f"{parent}{separator}{current}")
        else:
            results.append(current)
    return results
