"""Transform registry for discovering and constructing transforms."""

from __future__ import annotations

from typing import TypeVar

from renfield.transforms.base import Transform
from renfield.transforms.case import CaseTransform
from renfield.transforms.postpend import PostpendTransform
from renfield.transforms.prepend import PrependTransform
from renfield.transforms.replace import ReplaceTransform
from renfield.transforms.sub_regex import SubRegexTransform

T = TypeVar("T", bound=Transform)

TRANSFORMS: dict[str, type[Transform]] = {
    PrependTransform().name: PrependTransform,
    PostpendTransform().name: PostpendTransform,
    ReplaceTransform().name: ReplaceTransform,
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
        "sub_regex": "Sub Regex",
        "case": "Case",
    }
    return [(name, labels.get(name, name)) for name in TRANSFORMS]


def create_transform(name: str) -> Transform:
    """Instantiate a new transform by registry key."""
    cls = TRANSFORMS[name]
    return cls.from_fields({})
