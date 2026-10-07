"""Apply an ordered list of transforms to filenames."""

from __future__ import annotations

from .transforms.base import Transform, TransformError, split_stem

#: Shown in the preview column when any transform in the chain is not valid.
INVALID_PREVIEW = "Invalid"


def apply_transforms(
    filenames: list[str],
    transforms: list[Transform],
    *,
    ignore_extension: bool = True,
) -> list[str]:
    """Apply each transform to each filename basename, in list order.

    When ignore_extension is False, the last "." in the basename marks the
    extension. Transforms then apply only to the base name and the engine
    reattaches the extension. When True, transforms apply to the whole
    basename.

    If a transform is not valid, the chain short-circuits and every preview
    entry becomes the unmodified sentinel "Invalid".
    """
    if not transforms:
        return list(filenames)

    results: list[str] = []
    for file_index, filename in enumerate(filenames):
        parent, separator, basename = filename.rpartition("/")
        if ignore_extension:
            stem, suffix = basename, ""
        else:
            stem, suffix = split_stem(basename)
        current = stem
        try:
            for transform in transforms:
                current = transform.apply(current, file_index)
        except TransformError:
            return [INVALID_PREVIEW for _ in filenames]
        combined = f"{current}{suffix}"
        if separator:
            results.append(f"{parent}{separator}{combined}")
        else:
            results.append(combined)
    return results
