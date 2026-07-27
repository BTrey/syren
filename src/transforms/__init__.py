"""Transform registry for discovering and constructing transforms."""

from __future__ import annotations

from typing import TypeVar

from .base import Transform
from .case import CaseTransform
from .postpend import PostpendTransform
from .prepend import PrependTransform
from .range import RangeTransform
from .replace import ReplaceTransform
from .sub_regex import SubRegexTransform

T = TypeVar("T", bound=Transform)

TRANSFORMS: dict[str, type[Transform]] = {
    PrependTransform().name: PrependTransform,
    PostpendTransform().name: PostpendTransform,
    ReplaceTransform().name: ReplaceTransform,
    RangeTransform().name: RangeTransform,
    SubRegexTransform().name: SubRegexTransform,
    CaseTransform().name: CaseTransform,
}


def register_transform(cls: type[T]) -> type[T]:
    """Register a transform class so it appears in the add-transform menu."""
    instance = cls()
    TRANSFORMS[instance.name] = cls
    return cls


def transform_labels() -> list[tuple[str, str]]:
    """Return (registry key, display label) pairs for the UI menu."""
    labels = {
        "prepend": "Prepend",
        "postpend": "Postpend",
        "replace": "Replace",
        "range": "Range",
        "sub_regex": "Sub Regex",
        "case": "Case",
    }
    return [(name, labels.get(name, name)) for name in TRANSFORMS]


MENU_HIGHLIGHT_COLOR = "#b58900"


def transform_menu_options() -> list[tuple[str, str]]:
    """Return transform menu entries sorted alphabetically by label."""
    return sorted(transform_labels(), key=lambda item: item[1].casefold())


def format_transform_menu_label(label: str) -> str:
    """Highlight the first letter of a transform menu label."""
    if not label:
        return label
    return f"[bold {MENU_HIGHLIGHT_COLOR}]{label[0]}[/]{label[1:]}"


def jump_to_menu_letter(
    options: list[tuple[str, str]],
    letter: str,
    *,
    current_index: int | None,
    last_letter: str | None,
) -> tuple[int | None, str | None]:
    """Return the option index and updated last letter for letter navigation."""
    normalized = letter.casefold()
    matches = [
        index
        for index, (_, label) in enumerate(options)
        if label[:1].casefold() == normalized
    ]
    if not matches:
        return current_index, last_letter

    if last_letter == normalized and current_index in matches:
        position = matches.index(current_index)
        target = matches[(position + 1) % len(matches)]
    else:
        target = matches[0]

    return target, normalized


def create_transform(name: str) -> Transform:
    """Instantiate a new transform by registry key."""
    cls = TRANSFORMS[name]
    return cls.from_fields({})
