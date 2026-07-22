"""Prepend text to filenames, with optional #NNN auto-increment."""

from __future__ import annotations

from dataclasses import dataclass

from renfield.transforms.base import FieldSpec, Transform, expand_numbered


@dataclass
class PrependTransform(Transform):
    text: str = ""

    @property
    def name(self) -> str:
        return "prepend"

    def apply(self, filename: str, file_index: int) -> str:
        prefix = expand_numbered(self.text, file_index)
        return prefix + filename

    def field_specs(self) -> tuple[FieldSpec, ...]:
        return (FieldSpec("text", "Prepend text"),)

    def get_field(self, key: str) -> str:
        if key == "text":
            return self.text
        raise KeyError(key)

    def set_field(self, key: str, value: str) -> None:
        if key == "text":
            self.text = value
            return
        raise KeyError(key)

    @classmethod
    def from_fields(cls, fields: dict[str, str]) -> PrependTransform:
        return cls(text=fields.get("text", ""))
