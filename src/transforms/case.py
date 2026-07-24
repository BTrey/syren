"""Change letter case on the filename stem."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .base import FieldSpec, FieldType, Transform, split_stem

CASE_MODES = frozenset({"UPPER", "lower", "sentence", "title"})
CASE_SELECT_OPTIONS: tuple[tuple[str, str], ...] = (
    ("UPPER", "UPPER"),
    ("lower", "lower"),
    ("Sentence", "sentence"),
    ("Title Case", "title"),
)


def _capitalize_word(word: str) -> str:
    lowered = word.lower()
    for index, character in enumerate(lowered):
        if character.isalpha():
            return lowered[:index] + character.upper() + lowered[index + 1 :]
    return word


def apply_title_case(stem: str) -> str:
    """Capitalize each alphanumeric word; non-alphanumeric characters are separators."""
    if not stem:
        return stem
    pieces = re.split(r"([^0-9A-Za-z]+)", stem)
    result: list[str] = []
    for index, piece in enumerate(pieces):
        if not piece:
            continue
        if index % 2 == 0:
            result.append(_capitalize_word(piece))
        else:
            result.append(piece)
    return "".join(result)


def apply_case(stem: str, mode: str) -> str:
    if mode == "UPPER":
        return stem.upper()
    if mode == "lower":
        return stem.lower()
    if mode == "sentence":
        if not stem:
            return stem
        return stem[0].upper() + stem[1:].lower()
    if mode == "title":
        return apply_title_case(stem)
    return stem


@dataclass
class CaseTransform(Transform):
    mode: str = "lower"

    @property
    def name(self) -> str:
        return "case"

    def apply(self, filename: str, file_index: int) -> str:
        stem, suffix = split_stem(filename)
        return apply_case(stem, self.mode) + suffix

    def field_specs(self) -> tuple[FieldSpec, ...]:
        return (
            FieldSpec(
                "mode",
                "Case",
                field_type=FieldType.SELECT,
                options=tuple(mode for _, mode in CASE_SELECT_OPTIONS),
                select_options=CASE_SELECT_OPTIONS,
            ),
        )

    def get_field(self, key: str) -> str:
        if key == "mode":
            return self.mode
        raise KeyError(key)

    def set_field(self, key: str, value: str) -> None:
        if key == "mode":
            self.mode = value if value in CASE_MODES else "lower"
            return
        raise KeyError(key)

    @classmethod
    def from_fields(cls, fields: dict[str, str]) -> CaseTransform:
        mode = fields.get("mode", "lower")
        if mode not in CASE_MODES:
            mode = "lower"
        return cls(mode=mode)
