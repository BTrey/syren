"""Apply an ordered list of transforms to filenames."""

from __future__ import annotations

from .transforms.base import Transform, TransformError

#: Shown in the preview column when any transform in the chain is not valid.
INVALID_PREVIEW = "Invalid"


def apply_transforms(
    filenames: list[str],
    transforms: list[Transform],
) -> list[str]:
    """Apply each transform to each filename basename, in list order.

    If a transform is not valid, the chain short-circuits and every preview
    entry becomes the unmodified sentinel "Invalid".
    """
    if not transforms:
        return list(filenames)

    results: list[str] = []
    for file_index, filename in enumerate(filenames):
        parent, separator, basename = filename.rpartition("/")
        current = basename
        try:
            for transform in transforms:
                current = transform.apply(current, file_index)
        except TransformError:
            return [INVALID_PREVIEW for _ in filenames]
        if separator:
            results.append(f"{parent}{separator}{current}")
        else:
            results.append(current)
    return results
