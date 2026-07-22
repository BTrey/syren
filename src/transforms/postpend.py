"""Append text to filenames, with optional #NNN auto-increment."""

from __future__ import annotations

from dataclasses import dataclass

from .base import FieldSpec, Transform, expand_numbered


@dataclass
class PostpendTransform(Transform):
    text: str = ""

    @property
    def name(self) -> str:
        return "postpend"

    def apply(self, filename: str, file_index: int) -> str:
        suffix = expand_numbered(self.text, file_index)
        return filename + suffix

    def field_specs(self) -> tuple[FieldSpec, ...]:
        return (FieldSpec("text", "Postpend text"),)

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
    def from_fields(cls, fields: dict[str, str]) -> PostpendTransform:
        return cls(text=fields.get("text", ""))
