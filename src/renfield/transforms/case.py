"""Change letter case on the filename stem."""

from __future__ import annotations

from dataclasses import dataclass

from renfield.transforms.base import FieldSpec, FieldType, Transform, split_stem

CASE_OPTIONS = ("UPPER", "lower", "sentence")


def apply_case(stem: str, mode: str) -> str:
    if mode == "UPPER":
        return stem.upper()
    if mode == "lower":
        return stem.lower()
    if mode == "sentence":
        if not stem:
            return stem
        return stem[0].upper() + stem[1:].lower()
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
                options=CASE_OPTIONS,
            ),
        )

    def get_field(self, key: str) -> str:
        if key == "mode":
            return self.mode
        raise KeyError(key)

    def set_field(self, key: str, value: str) -> None:
        if key == "mode":
            self.mode = value if value in CASE_OPTIONS else "lower"
            return
        raise KeyError(key)

    @classmethod
    def from_fields(cls, fields: dict[str, str]) -> CaseTransform:
        mode = fields.get("mode", "lower")
        if mode not in CASE_OPTIONS:
            mode = "lower"
        return cls(mode=mode)
